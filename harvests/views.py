"""
Views for managing grape harvests and juice allocations in the wine production system.

This module provides views for recording grape harvests, tracking juice yields,
and managing juice allocations to tanks. It includes functionality for monitoring
harvest status and managing the flow of juice through the production process.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import F, ExpressionWrapper, DecimalField, Q, Sum, Value, FloatField
from django.db.models.functions import Coalesce
from core.utils.exceptions import log_error
from .models import Harvest, HarvestAllocation
from .forms import HarvestForm, HarvestAllocationForm
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class HarvestListView(LoginRequiredMixin, ListView):
    """
    Display a list of all harvests with search and filter functionality.
    
    Shows harvests with their key information including date, vineyard, quantity,
    and juice status. Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - harvests: QuerySet of filtered harvests
        - search_query: Current search term if any
        - active_tab: Current active navigation tab
    """
    model = Harvest
    template_name = 'harvests/list_harvests.html'
    context_object_name = 'harvests'
    ordering = ['-date']

    def get_queryset(self):
        try:
            # Start with all harvests, ordered by date
            queryset = super().get_queryset()
            
            # Calculate allocated volume for each harvest
            allocated_volume = Coalesce(
                Sum('allocations__allocated_volume', output_field=DecimalField()), 
                Value(0, output_field=DecimalField())
            )
            
            # Annotate the queryset with allocated volume and remaining juice
            queryset = queryset.annotate(
                allocated_volume=allocated_volume,
                remaining_juice=ExpressionWrapper(
                    F('quantity') - F('allocated_volume'),
                    output_field=DecimalField()
                )
            )
            
            # Get search query from request parameters
            search_query = self.request.GET.get('search', '').strip()
            
            if search_query:
                # Apply search filter across multiple fields
                queryset = queryset.filter(
                    Q(vineyard__name__icontains=search_query) |
                    Q(notes__icontains=search_query)
                )
            
            return queryset.order_by(self.ordering[0])
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['search_query'] = self.request.GET.get('search', '')
            context['active_tab'] = 'harvests'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise


class HarvestDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a specific harvest.
    
    Shows all harvest information including juice allocations and remaining
    juice. Uses select_related and prefetch_related to optimize queries.

    Args:
        request: The HTTP request object
        pk: ID of the harvest to display

    Returns:
        Rendered template with detailed harvest information
    """
    model = Harvest
    template_name = 'harvests/harvest_detail.html'
    context_object_name = 'harvest'

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.select_related(
                    'vineyard',
                    'created_by'
                ).prefetch_related(
                    'allocations',
                    'allocations__tank'
                ),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Harvest not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Harvest with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'harvests'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise


class HarvestCreateView(LoginRequiredMixin, CreateView):
    """
    Display and process the form for recording a new harvest.
    
    Handles both GET requests to display the form and POST requests to create
    a new harvest record. Validates input and calculates initial values.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to harvest list
        On invalid POST: Rendered form template with errors
    """
    model = Harvest
    form_class = HarvestForm
    template_name = 'harvests/harvest_form.html'
    success_url = reverse_lazy('harvests:list_harvests')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'harvests'
            context['title'] = 'Add New Harvest'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            form.instance.full_clean()
            response = super().form_valid(form)

            logger.info("New harvest created", extra={
                'user': self.request.user.username,
                'harvest_id': form.instance.id,
                'vineyard': form.instance.vineyard.name,
                'quantity': form.instance.quantity
            })

            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class HarvestUpdateView(LoginRequiredMixin, UpdateView):
    """
    Display and process the form for editing an existing harvest.
    
    Handles both GET requests to display the pre-populated form and POST
    requests to update the harvest. Validates changes against existing
    juice allocations.

    Args:
        request: The HTTP request object
        pk: ID of the harvest to edit

    Returns:
        On GET: Rendered form template with pre-populated data
        On successful POST: Redirect to harvest detail
        On invalid POST: Rendered form template with errors
    """
    model = Harvest
    form_class = HarvestForm
    template_name = 'harvests/harvest_form.html'

    def get_success_url(self):
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.select_related(
                    'vineyard',
                    'created_by'
                ).prefetch_related(
                    'allocations',
                    'allocations__tank'
                ),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Harvest not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Harvest with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'harvests'
            context['title'] = f'Edit Harvest: {self.object}'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.updated_by = self.request.user
            form.instance.full_clean()
            response = super().form_valid(form)

            logger.info("Harvest updated", extra={
                'user': self.request.user.username,
                'harvest_id': form.instance.id,
                'vineyard': form.instance.vineyard.name,
                'quantity': form.instance.quantity
            })

            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class HarvestDeleteView(LoginRequiredMixin, DeleteView):
    """
    Display and process the form for deleting an existing harvest.
    
    Handles both GET requests to display the confirmation form and POST
    requests to delete the harvest.

    Args:
        request: The HTTP request object
        pk: ID of the harvest to delete

    Returns:
        On GET: Rendered confirmation form template
        On successful POST: Redirect to harvest list
    """
    model = Harvest
    template_name = 'harvests/harvest_confirm_delete.html'
    success_url = reverse_lazy('harvests:list_harvests')


class HarvestAllocationCreateView(LoginRequiredMixin, CreateView):
    """
    Display and process the form for adding a new juice allocation.
    
    Handles allocation of juice from a harvest to a specific tank. Validates
    that allocation doesn't exceed available juice or tank capacity.

    Args:
        request: The HTTP request object
        harvest_id: ID of the harvest to allocate from

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to harvest detail
        On invalid POST: Rendered form template with errors
    """
    model = HarvestAllocation
    form_class = HarvestAllocationForm
    template_name = 'harvests/allocation_form.html'

    def get_success_url(self):
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.harvest.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.harvest = get_object_or_404(Harvest, pk=self.kwargs.get('harvest_id'))
        kwargs['harvest'] = self.harvest
        return kwargs

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'harvests'
            context['title'] = f'Add Allocation from {self.harvest}'
            context['harvest'] = self.harvest
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            form.instance.harvest = self.harvest
            form.instance.full_clean()
            response = super().form_valid(form)

            logger.info("New harvest allocation created", extra={
                'user': self.request.user.username,
                'allocation_id': form.instance.id,
                'harvest_id': form.instance.harvest.id,
                'tank_id': form.instance.tank.id,
                'volume': form.instance.allocated_volume
            })

            return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, str(e))
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class HarvestAllocationDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a specific juice allocation.
    
    Shows all allocation information including harvest and tank details.

    Args:
        request: The HTTP request object
        pk: ID of the allocation to display

    Returns:
        Rendered template with detailed allocation information
    """
    model = HarvestAllocation
    template_name = 'harvests/allocation_detail.html'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except HarvestAllocation.DoesNotExist:
            raise Http404(f"Allocation with id {self.kwargs['pk']} not found")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'harvests'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise


class HarvestAllocationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Display and process the form for editing an existing juice allocation.
    
    Handles both GET requests to display the pre-populated form and POST
    requests to update the allocation. Validates changes against existing
    juice allocations.

    Args:
        request: The HTTP request object
        pk: ID of the allocation to edit

    Returns:
        On GET: Rendered form template with pre-populated data
        On successful POST: Redirect to allocation detail
        On invalid POST: Rendered form template with errors
    """
    model = HarvestAllocation
    form_class = HarvestAllocationForm
    template_name = 'harvests/allocation_form.html'

    def get_success_url(self):
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.object.harvest.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['harvest'] = self.object.harvest
        return kwargs

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['harvest'] = self.object.harvest
            context['active_tab'] = 'harvests'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        """Handle valid form submission."""
        try:
            form.instance.updated_by = self.request.user
            # Save the form to update the allocation
            response = super().form_valid(form)
            
            # Log the update
            logger.info("Harvest allocation updated", extra={
                'user': self.request.user.username,
                'allocation_id': self.object.id,
                'harvest_id': self.object.harvest.id,
                'tank_id': self.object.tank.id,
                'volume': self.object.allocated_volume
            })
            
            messages.success(self.request, 'Allocation updated successfully.')
            return response
            
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            messages.error(self.request, 'An error occurred while updating the allocation.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except HarvestAllocation.DoesNotExist:
            raise Http404(f"Allocation with id {self.kwargs['pk']} not found")


class HarvestAllocationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Display and process the form for deleting an existing juice allocation.
    
    Handles both GET requests to display the confirmation form and POST
    requests to delete the allocation.

    Args:
        request: The HTTP request object
        pk: ID of the allocation to delete

    Returns:
        On GET: Rendered confirmation form template
        On successful POST: Redirect to harvest detail
    """
    model = HarvestAllocation
    template_name = 'harvests/allocation_confirm_delete.html'

    def get_success_url(self):
        """Return to the harvest detail page after deletion."""
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.object.harvest.pk})

    def delete(self, request, *args, **kwargs):
        """Delete the allocation and update the tank volume."""
        from cellars.models import TankHistory
        
        self.object = self.get_object()
        harvest_id = self.object.harvest.pk
        
        try:
            # Remove the allocated volume from the tank
            self.object.tank.update_volume(-float(self.object.allocated_volume))
            
            # Create history record for volume removal
            TankHistory.objects.create(
                tank=self.object.tank,
                operation_type='allocation',
                date=self.object.allocation_date,
                volume=-float(self.object.allocated_volume),
                harvest=self.object.harvest,
                created_by=request.user,
                notes=f"Deleted allocation of {self.object.allocated_volume}L"
            )
            
            # Delete the allocation
            self.object.delete()
            
            messages.success(request, 'Allocation deleted successfully.')
            return HttpResponseRedirect(self.get_success_url())
            
        except Exception as e:
            log_error(e, request)
            messages.error(request, 'An error occurred while deleting the allocation.')
            return HttpResponseRedirect(reverse('harvests:harvest_detail', kwargs={'pk': harvest_id}))


class HarvestAllocationListView(LoginRequiredMixin, ListView):
    """Display a list of harvest allocations."""
    model = HarvestAllocation
    template_name = 'harvests/allocation_list.html'
    context_object_name = 'allocations'
    
    def get_queryset(self):
        """Return all harvest allocations."""
        return HarvestAllocation.objects.all().select_related('harvest', 'tank')
