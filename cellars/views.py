from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import F, ExpressionWrapper, DecimalField, Q, Sum, Value, FloatField
from django.db.models.functions import Coalesce
from core.utils.exceptions import (
    handle_view_exception,
    InvalidOperationError,
    ResourceNotFoundError,
    ValidationError,
    log_error
)
from .models import Cellar, Tank, CrushedJuiceAllocation, TankHistory
from .forms import TankForm
import logging
from django import forms

logger = logging.getLogger('vinco')

class CellarListView(LoginRequiredMixin, ListView):
    model = Cellar
    template_name = 'cellars/list_cellars.html'
    context_object_name = 'cellars'
    ordering = ['name']

    def get_queryset(self):
        try:
            return super().get_queryset().order_by(*self.ordering)
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'cellars'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

class CellarDetailView(LoginRequiredMixin, DetailView):
    model = Cellar
    template_name = 'cellars/cellar_detail.html'
    context_object_name = 'cellar'

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.prefetch_related('tanks'),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Cellar not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Cellar with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'cellars'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

class CellarCreateView(LoginRequiredMixin, CreateView):
    model = Cellar
    template_name = 'cellars/cellar_form.html'
    fields = ['name', 'location', 'capacity', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'cellars'
            context['title'] = 'Add New Cellar'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.full_clean()  # Run model validation
            response = super().form_valid(form)

            logger.info("New cellar created", extra={
                'user': self.request.user.username,
                'cellar_id': form.instance.id,
                'cellar_name': form.instance.name,
                'capacity': form.instance.capacity
            })

            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

class CellarUpdateView(LoginRequiredMixin, UpdateView):
    model = Cellar
    template_name = 'cellars/cellar_form.html'
    fields = ['name', 'location', 'capacity', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(self.model, pk=pk)
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Cellar not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Cellar with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'cellars'
            context['title'] = f'Edit Cellar: {self.object.name}'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.full_clean()  # Run model validation
            response = super().form_valid(form)

            logger.info("Cellar updated", extra={
                'user': self.request.user.username,
                'cellar_id': form.instance.id,
                'cellar_name': form.instance.name,
                'capacity': form.instance.capacity
            })

            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

class TankListView(LoginRequiredMixin, ListView):
    model = Tank
    template_name = 'cellars/tank_list.html'
    context_object_name = 'tanks'

    def get_queryset(self):
        return Tank.objects.all().select_related('cellar')

class TankDetailView(LoginRequiredMixin, DetailView):
    model = Tank
    template_name = 'cellars/tank_detail.html'
    context_object_name = 'tank'

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.select_related('cellar').prefetch_related(
                    'crushed_juice_allocations',
                    'crushed_juice_allocations__harvest',
                    'crushed_juice_allocations__created_by'
                ),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Tank not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Tank with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'tanks'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

class TankCreateView(LoginRequiredMixin, CreateView):
    model = Tank
    form_class = TankForm
    template_name = 'cellars/tank_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.cellar = get_object_or_404(Cellar, pk=self.kwargs['cellar_id'])
        kwargs['cellar'] = self.cellar
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            form.instance.cellar = self.cellar
            response = super().form_valid(form)

            logger.info("New tank created", extra={
                'user': self.request.user.username,
                'tank_id': form.instance.id,
                'tank_name': form.instance.name,
                'cellar_id': form.instance.cellar.id,
                'capacity': form.instance.capacity
            })

            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def get_success_url(self):
        return reverse_lazy('cellars:cellar_detail', kwargs={'pk': self.cellar.pk})

class TankUpdateView(LoginRequiredMixin, UpdateView):
    model = Tank
    form_class = TankForm
    template_name = 'cellars/tank_form.html'

    def get_success_url(self):
        return reverse_lazy('cellars:cellar_detail', kwargs={'pk': self.object.cellar.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cellar'] = self.object.cellar
        return kwargs

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(self.model, pk=pk)
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Tank not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Tank with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'tanks'
            context['title'] = f'Edit Tank: {self.object.name}'
            context['cellar'] = self.object.cellar
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            form.instance.updated_by = self.request.user
            response = super().form_valid(form)

            logger.info("Tank updated", extra={
                'user': self.request.user.username,
                'tank_id': form.instance.id,
                'tank_name': form.instance.name,
                'cellar_id': form.instance.cellar.id,
                'capacity': form.instance.capacity,
                'current_volume': form.instance.current_volume
            })

            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

class TankHistoryView(LoginRequiredMixin, DetailView):
    model = Tank
    template_name = 'cellars/tank_history.html'
    context_object_name = 'tank'

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.select_related('cellar').prefetch_related(
                    'crushed_juice_allocations',
                    'crushed_juice_allocations__harvest',
                    'crushed_juice_allocations__created_by'
                ),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Tank not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Tank with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'tanks'
            context['title'] = f'Tank History: {self.object.name}'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

class TankTransferView(LoginRequiredMixin, FormView):
    template_name = 'cellars/tank_transfer_form.html'
    success_url = reverse_lazy('cellars:list_tanks')
    form_class = None

    def get_form_class(self):
        class TankTransferForm(forms.Form):
            source_tank = forms.ModelChoiceField(
                queryset=Tank.objects.all(),
                label='Source Tank'
            )
            target_tank = forms.ModelChoiceField(
                queryset=Tank.objects.all(),
                label='Target Tank'
            )
            volume = forms.DecimalField(
                min_value=0,
                label='Volume to Transfer (L)'
            )
            transfer_date = forms.DateField(
                label='Transfer Date'
            )

            def clean(self):
                cleaned_data = super().clean()
                source_tank = cleaned_data.get('source_tank')
                target_tank = cleaned_data.get('target_tank')
                volume = cleaned_data.get('volume')

                if not all([source_tank, target_tank, volume]):
                    return cleaned_data

                if source_tank == target_tank:
                    raise ValidationError("Source and target tanks must be different")

                if volume > source_tank.current_volume:
                    raise ValidationError(
                        f"Transfer volume ({volume} L) cannot exceed source tank's current volume "
                        f"({source_tank.current_volume} L)"
                    )

                available_space = target_tank.capacity - target_tank.current_volume
                if volume > available_space:
                    raise ValidationError(
                        f"Transfer volume ({volume} L) exceeds target tank's available space "
                        f"({available_space} L)"
                    )

                return cleaned_data

        return TankTransferForm

    def form_valid(self, form):
        try:
            source_tank = form.cleaned_data['source_tank']
            target_tank = form.cleaned_data['target_tank']
            volume = form.cleaned_data['volume']
            transfer_date = form.cleaned_data['transfer_date']

            # Create history entries for both tanks
            TankHistory.objects.create(
                tank=source_tank,
                operation_type='transfer_out',
                date=transfer_date,
                volume=-volume,
                destination=target_tank,
                created_by=self.request.user
            )

            TankHistory.objects.create(
                tank=target_tank,
                operation_type='transfer_in',
                date=transfer_date,
                volume=volume,
                source=source_tank,
                created_by=self.request.user
            )

            # Update tank volumes
            source_tank.current_volume = source_tank.current_volume - volume
            target_tank.current_volume = target_tank.current_volume + volume

            source_tank.save()
            target_tank.save()

            logger.info("Wine transfer completed", extra={
                'user': self.request.user.username,
                'source_tank_id': source_tank.id,
                'target_tank_id': target_tank.id,
                'volume': volume,
                'transfer_date': transfer_date
            })

            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

class CellarDeleteView(LoginRequiredMixin, UpdateView):
    model = Cellar
    template_name = 'cellars/cellar_confirm_delete.html'
    success_url = reverse_lazy('cellars:list_cellars')

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(self.model, pk=pk)
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Cellar not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Cellar with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'cellars'
            context['title'] = f'Delete Cellar: {self.object.name}'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def post(self, request, *args, **kwargs):
        try:
            cellar = self.get_object()
            cellar_name = cellar.name
            cellar_id = cellar.id
            
            if cellar.tanks.exists():
                raise InvalidOperationError(
                    "Cannot delete cellar that contains tanks. Remove all tanks first."
                )
                
            cellar.delete()
            
            logger.info("Cellar deleted", extra={
                'user': request.user.username,
                'cellar_id': cellar_id,
                'cellar_name': cellar_name
            })
            
            return HttpResponseRedirect(self.success_url)
        except InvalidOperationError:
            raise
        except Exception as e:
            log_error(e, request)
            raise

class TankDeleteView(LoginRequiredMixin, UpdateView):
    model = Tank
    template_name = 'cellars/tank_confirm_delete.html'
    success_url = reverse_lazy('cellars:list_tanks')

    def get_object(self, queryset=None):
        try:
            pk = self.kwargs.get(self.pk_url_kwarg)
            obj = get_object_or_404(
                self.model.objects.select_related('cellar'),
                pk=pk
            )
            return obj
        except self.model.DoesNotExist:
            logger.warning(f"Tank not found: {pk}", extra={
                'user': self.request.user.username
            })
            raise ResourceNotFoundError(f"Tank with id {pk} not found")
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'tanks'
            context['title'] = f'Delete Tank: {self.object.name}'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def post(self, request, *args, **kwargs):
        try:
            tank = self.get_object()
            tank_name = tank.name
            tank_id = tank.id
            cellar_id = tank.cellar.id
            
            if tank.current_volume > 0:
                raise InvalidOperationError(
                    "Cannot delete tank that contains wine. Empty the tank first."
                )
                
            tank.delete()
            
            logger.info("Tank deleted", extra={
                'user': request.user.username,
                'tank_id': tank_id,
                'tank_name': tank_name,
                'cellar_id': cellar_id
            })
            
            return HttpResponseRedirect(self.success_url)
        except InvalidOperationError:
            raise
        except Exception as e:
            log_error(e, request)
            raise

class AllocationListView(LoginRequiredMixin, ListView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/list_allocations.html'
    context_object_name = 'allocations'
    ordering = ['-allocation_date']

    def get_queryset(self):
        try:
            return super().get_queryset().select_related(
                'harvest', 'tank', 'tank__cellar'
            ).order_by(*self.ordering)
        except Exception as e:
            log_error(e, self.request)
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'allocations'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

class AllocationCreateView(LoginRequiredMixin, CreateView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/allocation_form.html'
    fields = ['harvest', 'tank', 'allocated_volume', 'allocation_date', 'notes']
    success_url = reverse_lazy('cellars:list_allocations')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'allocations'
            context['title'] = 'Add New Allocation'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            # Check if allocation would exceed tank capacity
            tank = form.cleaned_data['tank']
            tank_allocated = tank.crushed_juice_allocations.aggregate(
                total=Sum('allocated_volume')
            )['total'] or 0
            
            if tank_allocated + form.cleaned_data['allocated_volume'] > tank.capacity:
                logger.warning("Allocation failed - would exceed tank capacity", extra={
                    'user': self.request.user.username,
                    'tank_id': tank.id,
                    'requested_volume': form.cleaned_data['allocated_volume'],
                    'available_capacity': tank.capacity - tank_allocated
                })
                raise InvalidOperationError(
                    "Allocation would exceed tank capacity"
                )

            form.instance.created_by = self.request.user
            response = super().form_valid(form)

            logger.info("New juice allocation created", extra={
                'user': self.request.user.username,
                'allocation_id': form.instance.id,
                'tank_id': tank.id,
                'harvest_id': form.instance.harvest.id,
                'allocated_volume': form.instance.allocated_volume
            })

            return response
        except InvalidOperationError:
            raise
        except Exception as e:
            log_error(e, self.request)
            raise

class TransferWineView(LoginRequiredMixin, CreateView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/transfer_wine.html'
    fields = ['source_tank', 'destination_tank', 'volume', 'transfer_date', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['active_tab'] = 'transfers'
            context['title'] = 'Transfer Wine'
            return context
        except Exception as e:
            log_error(e, self.request)
            raise

    def form_valid(self, form):
        try:
            source_tank = form.cleaned_data['source_tank']
            destination_tank = form.cleaned_data['destination_tank']
            volume = form.cleaned_data['volume']

            # Check if source tank has enough wine
            source_volume = source_tank.crushed_juice_allocations.aggregate(
                total=Sum('allocated_volume')
            )['total'] or 0
            
            if volume > source_volume:
                logger.warning("Transfer failed - insufficient volume in source tank", extra={
                    'user': self.request.user.username,
                    'source_tank_id': source_tank.id,
                    'requested_volume': volume,
                    'available_volume': source_volume
                })
                raise InvalidOperationError(
                    "Insufficient volume in source tank"
                )

            # Check if destination tank has enough capacity
            dest_volume = destination_tank.crushed_juice_allocations.aggregate(
                total=Sum('allocated_volume')
            )['total'] or 0
            
            if dest_volume + volume > destination_tank.capacity:
                logger.warning("Transfer failed - insufficient capacity in destination tank", extra={
                    'user': self.request.user.username,
                    'destination_tank_id': destination_tank.id,
                    'requested_volume': volume,
                    'available_capacity': destination_tank.capacity - dest_volume
                })
                raise InvalidOperationError(
                    "Insufficient capacity in destination tank"
                )

            form.instance.created_by = self.request.user
            response = super().form_valid(form)

            logger.info("Wine transfer completed", extra={
                'user': self.request.user.username,
                'transfer_id': form.instance.id,
                'source_tank_id': source_tank.id,
                'destination_tank_id': destination_tank.id,
                'volume': volume
            })

            return response
        except InvalidOperationError:
            raise
        except Exception as e:
            log_error(e, self.request)
            raise
