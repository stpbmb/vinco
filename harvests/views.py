"""
Views for managing grape harvests and juice allocations in the wine production system.

This module provides views for recording grape harvests, tracking juice yields,
and managing juice allocations to tanks. It includes functionality for monitoring
harvest status and managing the flow of juice through the production process.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import F, ExpressionWrapper, DecimalField, Q, Sum, Value, FloatField
from django.db.models.functions import Coalesce
from .models import Harvest, HarvestAllocation
from .forms import HarvestForm, HarvestAllocationForm

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
        # Start with all harvests, ordered by date
        harvests = Harvest.objects.annotate(
            allocated_volume_sum=Coalesce(
                Sum('harvest_allocations__allocated_volume'), 
                Value(0, output_field=FloatField())
            )
        )
        
        # Get search query from request parameters
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            # Apply search filter across multiple fields
            harvests = harvests.filter(
                Q(vineyard__name__icontains=search_query) |
                Q(vineyard__location__icontains=search_query) |
                Q(vineyard__grape_variety__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        return harvests

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        # Get harvests that have juice yield but no allocations or not fully allocated
        unallocated_harvests = Harvest.objects.exclude(
            juice_yield__isnull=True
        ).annotate(
            allocated_volume_sum=Coalesce(
                Sum('harvest_allocations__allocated_volume'), 
                Value(0, output_field=FloatField())
            )
        ).annotate(
            remaining_volume=ExpressionWrapper(
                F('juice_yield') - F('allocated_volume_sum'),
                output_field=FloatField()
            )
        ).filter(
            Q(allocated_volume_sum__isnull=True) | 
            Q(remaining_volume__gt=0)
        ).order_by('-date')
        
        context['unallocated_harvests'] = unallocated_harvests
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        # Get allocations ordered by date
        context['allocations'] = self.object.harvest_allocations.select_related('tank').order_by('-allocation_date')
        return context

class HarvestCreateView(LoginRequiredMixin, CreateView):
    """
    Display and process the form for recording a new harvest.
    
    Handles both GET requests to display the form and POST requests to create
    a new harvest record. Validates input and calculates initial values.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to harvest detail
        On invalid POST: Rendered form template with errors
    """
    model = Harvest
    form_class = HarvestForm
    template_name = 'harvests/harvest_form.html'
    success_url = reverse_lazy('harvests:list_harvests')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        context['title'] = 'Add New Harvest'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

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
    success_url = reverse_lazy('harvests:list_harvests')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        context['title'] = 'Edit Harvest'
        return context

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

    def get_harvest(self):
        return get_object_or_404(Harvest, pk=self.kwargs['harvest_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['harvest'] = self.get_harvest()
        if kwargs.get('instance') is None:
            kwargs['instance'] = self.model(harvest=self.get_harvest())
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        context['harvest'] = self.get_harvest()
        context['title'] = f'Allocate Juice from {context["harvest"]}'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.kwargs['harvest_id']})
