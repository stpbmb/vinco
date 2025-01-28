from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import F, ExpressionWrapper, DecimalField, Q, Sum, Value, FloatField
from django.db.models.functions import Coalesce
from .models import Harvest, HarvestAllocation
from .forms import HarvestForm, HarvestAllocationForm

class HarvestListView(LoginRequiredMixin, ListView):
    model = Harvest
    template_name = 'harvests/list_harvests.html'
    context_object_name = 'harvests'
    ordering = ['-date']

    def get_queryset(self):
        return Harvest.objects.annotate(
            allocated_volume_sum=Coalesce(
                Sum('harvest_allocations__allocated_volume'), 
                Value(0, output_field=FloatField())
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        
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
