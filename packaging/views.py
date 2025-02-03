"""
Views for managing wine packaging operations and inventory tracking.

This module provides views for recording bottling operations, managing packaging
materials inventory, and tracking finished product quantities. It includes
functionality for monitoring packaging efficiency and material usage.
"""

import logging
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from core.utils.exceptions import (
    handle_view_exception,
    InvalidOperationError,
    ResourceNotFoundError,
    ValidationError,
    log_error
)
from .models import Bottle, Label, Closure, Box, Bottling
from .forms import BottleForm, LabelForm, ClosureForm, BoxForm, BottlingForm
from cellars.models import Tank
from core.views import TenantViewMixin

logger = logging.getLogger('vinco')

# Bottle Views
class BottleListView(TenantViewMixin, ListView):
    model = Bottle
    template_name = 'packaging/list_bottles.html'
    context_object_name = 'bottles'

class BottleDetailView(TenantViewMixin, DetailView):
    model = Bottle
    template_name = 'packaging/bottle_detail.html'
    context_object_name = 'bottle'

class BottleCreateView(TenantViewMixin, CreateView):
    model = Bottle
    form_class = BottleForm
    template_name = 'packaging/bottle_form.html'
    success_url = reverse_lazy('packaging:bottle-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

class BottleUpdateView(TenantViewMixin, UpdateView):
    model = Bottle
    form_class = BottleForm
    template_name = 'packaging/bottle_form.html'
    success_url = reverse_lazy('packaging:bottle-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

# Label Views
class LabelListView(TenantViewMixin, ListView):
    model = Label
    template_name = 'packaging/list_labels.html'
    context_object_name = 'labels'

class LabelDetailView(TenantViewMixin, DetailView):
    model = Label
    template_name = 'packaging/label_detail.html'
    context_object_name = 'label'

class LabelCreateView(TenantViewMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = 'packaging/label_form.html'
    success_url = reverse_lazy('packaging:label-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

class LabelUpdateView(TenantViewMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'packaging/label_form.html'
    success_url = reverse_lazy('packaging:label-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

# Closure Views
class ClosureListView(TenantViewMixin, ListView):
    model = Closure
    template_name = 'packaging/list_closures.html'
    context_object_name = 'closures'

class ClosureDetailView(TenantViewMixin, DetailView):
    model = Closure
    template_name = 'packaging/closure_detail.html'
    context_object_name = 'closure'

class ClosureCreateView(TenantViewMixin, CreateView):
    model = Closure
    form_class = ClosureForm
    template_name = 'packaging/closure_form.html'
    success_url = reverse_lazy('packaging:closure-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

class ClosureUpdateView(TenantViewMixin, UpdateView):
    model = Closure
    form_class = ClosureForm
    template_name = 'packaging/closure_form.html'
    success_url = reverse_lazy('packaging:closure-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

# Box Views
class BoxListView(TenantViewMixin, ListView):
    model = Box
    template_name = 'packaging/list_boxes.html'
    context_object_name = 'boxes'

class BoxDetailView(TenantViewMixin, DetailView):
    model = Box
    template_name = 'packaging/box_detail.html'
    context_object_name = 'box'

class BoxCreateView(TenantViewMixin, CreateView):
    model = Box
    form_class = BoxForm
    template_name = 'packaging/box_form.html'
    success_url = reverse_lazy('packaging:box-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

class BoxUpdateView(TenantViewMixin, UpdateView):
    model = Box
    form_class = BoxForm
    template_name = 'packaging/box_form.html'
    success_url = reverse_lazy('packaging:box-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

# Bottling Views
class BottlingListView(TenantViewMixin, ListView):
    model = Bottling
    template_name = 'packaging/list_bottlings.html'
    context_object_name = 'bottlings'

class BottlingDetailView(TenantViewMixin, DetailView):
    model = Bottling
    template_name = 'packaging/bottling_detail.html'
    context_object_name = 'bottling'

class BottlingCreateView(TenantViewMixin, CreateView):
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:bottling-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

class BottlingUpdateView(TenantViewMixin, UpdateView):
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:bottling-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

@login_required
@handle_view_exception
def list_unfinished_bottlings(request):
    """
    Display a list of all unfinished bottlings.
    
    Shows bottlings with their key information including date, bottle, and quantity.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - bottlings: QuerySet of filtered bottlings
        - title: Page title
    """
    try:
        bottlings = Bottling.objects.filter(status='unfinished').order_by('-bottling_date')
        context = {
            'bottlings': bottlings,
            'title': 'Unfinished Bottlings'
        }
        return render(request, 'packaging/list_unfinished.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def list_finished_bottlings(request):
    """
    Display a list of all finished bottlings.
    
    Shows bottlings with their key information including date, bottle, and quantity.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - bottlings: QuerySet of filtered bottlings
        - title: Page title
    """
    try:
        bottlings = Bottling.objects.exclude(
            Q(closure__isnull=True) | Q(label__isnull=True) | Q(box__isnull=True)
        ).order_by('-bottling_date')
        context = {
            'bottlings': bottlings,
            'title': 'Finished Bottlings'
        }
        return render(request, 'packaging/list_finished.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def delete_bottling(request, pk):
    """
    Delete a bottling record.
    
    Handles POST requests to delete a bottling record.
    Returns inventory to stock.

    Args:
        request: The HTTP request object
        pk: ID of the bottling to delete

    Returns:
        On POST: Redirect to bottling list
    """
    try:
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
            
        bottling = get_object_or_404(Bottling, pk=pk)
        
        # Return inventory to stock
        if bottling.bottle:
            bottling.bottle.stock += bottling.quantity
            bottling.bottle.save()
            
        if bottling.label:
            bottling.label.stock += bottling.quantity
            bottling.label.save()
            
        if bottling.closure:
            bottling.closure.stock += bottling.quantity
            bottling.closure.save()
            
        if bottling.box:
            bottling.box.stock += math.ceil(bottling.quantity / bottling.box.bottle_capacity)
            bottling.box.save()
            
        # Delete the bottling
        bottling.delete()
        
        messages.success(request, 'Bottling deleted successfully.')
        return redirect('packaging:list_unfinished')
    except Exception as e:
        log_error(e, request)
        raise
