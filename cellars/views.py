from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Cellar, Tank, CrushedJuiceAllocation

class CellarListView(LoginRequiredMixin, ListView):
    model = Cellar
    template_name = 'cellars/list_cellars.html'
    context_object_name = 'cellars'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        return context

class CellarDetailView(LoginRequiredMixin, DetailView):
    model = Cellar
    template_name = 'cellars/cellar_detail.html'
    context_object_name = 'cellar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        return context

class CellarCreateView(LoginRequiredMixin, CreateView):
    model = Cellar
    template_name = 'cellars/cellar_form.html'
    fields = ['name', 'location', 'capacity', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        context['title'] = 'Add New Cellar'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CellarUpdateView(LoginRequiredMixin, UpdateView):
    model = Cellar
    template_name = 'cellars/cellar_form.html'
    fields = ['name', 'location', 'capacity', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        context['title'] = 'Edit Cellar'
        return context

class TankListView(LoginRequiredMixin, ListView):
    model = Tank
    template_name = 'cellars/list_tanks.html'
    context_object_name = 'tanks'
    ordering = ['cellar', 'name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'tanks'
        return context

class TankDetailView(LoginRequiredMixin, DetailView):
    model = Tank
    template_name = 'cellars/tank_detail.html'
    context_object_name = 'tank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'tanks'
        context['history'] = self.object.history.all().order_by('-date', '-created_at')[:10]
        return context

class TankCreateView(LoginRequiredMixin, CreateView):
    model = Tank
    template_name = 'cellars/tank_form.html'
    fields = ['name', 'tank_type', 'capacity', 'notes']

    def get_cellar(self):
        return get_object_or_404(Cellar, pk=self.kwargs['cellar_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        context['cellar'] = self.get_cellar()
        context['title'] = f'Add New Tank to {context["cellar"].name}'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.cellar = self.get_cellar()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cellars:cellar_detail', kwargs={'pk': self.kwargs['cellar_id']})

class TankUpdateView(LoginRequiredMixin, UpdateView):
    model = Tank
    template_name = 'cellars/tank_form.html'
    fields = ['cellar', 'name', 'tank_type', 'capacity', 'notes']
    success_url = reverse_lazy('cellars:list_tanks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'tanks'
        context['title'] = 'Edit Tank'
        return context

class TankHistoryView(LoginRequiredMixin, DetailView):
    model = Tank
    template_name = 'cellars/tank_history.html'
    context_object_name = 'tank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        context['allocations'] = self.object.crushedjuiceallocation_set.all().order_by('-allocation_date')
        return context

class AllocationListView(LoginRequiredMixin, ListView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/list_allocations.html'
    context_object_name = 'allocations'
    ordering = ['-allocation_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'allocations'
        return context

class AllocationCreateView(LoginRequiredMixin, CreateView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/allocation_form.html'
    fields = ['harvest', 'tank', 'allocated_volume', 'allocation_date', 'notes']
    success_url = reverse_lazy('cellars:list_allocations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'allocations'
        context['title'] = 'Add New Allocation'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class TransferWineView(LoginRequiredMixin, CreateView):
    model = CrushedJuiceAllocation
    template_name = 'cellars/transfer_wine.html'
    fields = ['source_tank', 'destination_tank', 'volume', 'transfer_date', 'notes']
    success_url = reverse_lazy('cellars:list_cellars')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'cellars'
        context['title'] = 'Transfer Wine'
        
        # Pre-select source tank if provided in URL
        source_tank_id = self.request.GET.get('source')
        if source_tank_id:
            try:
                context['source_tank'] = Tank.objects.get(id=source_tank_id)
            except Tank.DoesNotExist:
                pass
                
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
