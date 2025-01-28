from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from .models import Harvest, HarvestAllocation
from .forms import HarvestForm, HarvestAllocationForm

class HarvestListView(LoginRequiredMixin, ListView):
    model = Harvest
    template_name = 'harvests/list_harvests.html'
    context_object_name = 'harvests'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        
        # Get harvests that have juice yield but no allocations or not fully allocated
        unallocated_harvests = Harvest.objects.exclude(
            juice_yield__isnull=True
        ).annotate(
            remaining_volume=ExpressionWrapper(
                F('juice_yield') - F('total_allocated_volume'),
                output_field=DecimalField()
            )
        ).filter(
            Q(total_allocated_volume__isnull=True) | 
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'harvests'
        context['harvest'] = self.get_harvest()
        context['title'] = f'Allocate Juice from {context["harvest"]}'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['harvest'] = self.get_harvest()
        return kwargs

    def form_valid(self, form):
        form.instance.harvest = self.get_harvest()
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Update tank volume
        form.instance.tank.update_volume(form.instance.allocated_volume)
        
        return response

    def get_success_url(self):
        return reverse_lazy('harvests:harvest_detail', kwargs={'pk': self.kwargs['harvest_id']})
