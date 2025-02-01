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
from django.views.generic import CreateView, UpdateView
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

logger = logging.getLogger('vinco')

# Bottle Views
@login_required
@handle_view_exception
def list_bottles(request):
    """
    Display a list of all bottles with search and filter functionality.
    
    Shows bottles with their key information including name, stock, and minimum stock.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - bottles: QuerySet of filtered bottles
        - low_stock: QuerySet of bottles with low stock
        - title: Page title
    """
    try:
        bottles = Bottle.objects.all()
        low_stock = bottles.filter(stock__lte=F('minimum_stock'))
        context = {
            'bottles': bottles,
            'low_stock': low_stock,
            'title': 'Bottles'
        }
        return render(request, 'packaging/list_bottles.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def bottle_detail(request, pk):
    """
    Display detailed information about a specific bottle.
    
    Shows all bottle information including name, stock, and minimum stock.

    Args:
        request: The HTTP request object
        pk: ID of the bottle to display

    Returns:
        Rendered template with detailed bottle information
    """
    try:
        bottle = get_object_or_404(Bottle, pk=pk)
        context = {
            'bottle': bottle,
            'title': f'Bottle: {bottle.name}'
        }
        return render(request, 'packaging/bottle_detail.html', context)
    except Bottle.DoesNotExist:
        logger.warning(f"Bottle not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Bottle with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def add_bottle(request):
    """
    Display and process the form for adding a new bottle.
    
    Handles both GET requests to display the form and POST requests to create
    a new bottle record. Validates input.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to bottle list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = BottleForm(request.POST)
            if form.is_valid():
                bottle = form.save(commit=False)
                bottle.created_by = request.user
                bottle.save()
                
                logger.info("New bottle created", extra={
                    'user': request.user.username,
                    'bottle_id': bottle.id,
                    'bottle_name': bottle.name
                })
                
                messages.success(request, 'Bottle added successfully.')
                return redirect('packaging:bottle_detail', pk=bottle.id)
            else:
                logger.warning("Bottle creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
        else:
            form = BottleForm()
            
        return render(request, 'packaging/bottle_form.html', {
            'form': form,
            'title': 'Add New Bottle'
        })
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def edit_bottle(request, pk):
    """
    Display and process the form for editing a bottle.
    
    Handles both GET requests to display the form and POST requests to update
    a bottle record. Validates input.

    Args:
        request: The HTTP request object
        pk: ID of the bottle to edit

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to bottle detail
        On invalid POST: Rendered form template with errors
    """
    try:
        bottle = get_object_or_404(Bottle, pk=pk)
        
        if request.method == 'POST':
            form = BottleForm(request.POST, instance=bottle)
            if form.is_valid():
                bottle = form.save()
                
                logger.info("Bottle updated", extra={
                    'user': request.user.username,
                    'bottle_id': bottle.id,
                    'bottle_name': bottle.name
                })
                
                messages.success(request, 'Bottle updated successfully.')
                return redirect('packaging:bottle_detail', pk=bottle.pk)
            else:
                return render(request, 'packaging/bottle_form.html', {
                    'form': form,
                    'title': f'Edit Bottle: {bottle.name}'
                }, status=400)
        else:
            form = BottleForm(instance=bottle)
            
        return render(request, 'packaging/bottle_form.html', {
            'form': form,
            'title': f'Edit Bottle: {bottle.name}'
        })
    except Bottle.DoesNotExist:
        logger.warning(f"Bottle not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Bottle with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def edit_label(request, pk):
    """
    Display and process the form for editing a label.
    
    Handles both GET requests to display the form and POST requests to update
    a label record. Validates input.

    Args:
        request: The HTTP request object
        pk: ID of the label to edit

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to label detail
        On invalid POST: Rendered form template with errors
    """
    try:
        label = get_object_or_404(Label, pk=pk)
        
        if request.method == 'POST':
            form = LabelForm(request.POST, request.FILES, instance=label)
            if form.is_valid():
                label = form.save()
                
                logger.info("Label updated", extra={
                    'user': request.user.username,
                    'label_id': label.id,
                    'label_name': label.name
                })
                
                messages.success(request, 'Label updated successfully.')
                return redirect('packaging:label_detail', pk=label.id)
            else:
                return render(request, 'packaging/label_form.html', {
                    'form': form,
                    'title': f'Edit Label: {label.name}'
                }, status=400)
        else:
            form = LabelForm(instance=label)
            
        return render(request, 'packaging/label_form.html', {
            'form': form,
            'title': f'Edit Label: {label.name}'
        })
    except Label.DoesNotExist:
        logger.warning(f"Label not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Label with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def edit_closure(request, pk):
    """
    Display and process the form for editing a closure.
    
    Handles both GET requests to display the form and POST requests to update
    a closure record. Validates input.

    Args:
        request: The HTTP request object
        pk: ID of the closure to edit

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to closure detail
        On invalid POST: Rendered form template with errors
    """
    try:
        closure = get_object_or_404(Closure, pk=pk)
        
        if request.method == 'POST':
            form = ClosureForm(request.POST, instance=closure)
            if form.is_valid():
                closure = form.save()
                
                logger.info("Closure updated", extra={
                    'user': request.user.username,
                    'closure_id': closure.id,
                    'closure_name': closure.name
                })
                
                messages.success(request, 'Closure updated successfully.')
                return redirect('packaging:closure_detail', pk=closure.id)
            else:
                return render(request, 'packaging/closure_form.html', {
                    'form': form,
                    'title': f'Edit Closure: {closure.name}'
                }, status=400)
        else:
            form = ClosureForm(instance=closure)
            
        return render(request, 'packaging/closure_form.html', {
            'form': form,
            'title': f'Edit Closure: {closure.name}'
        })
    except Closure.DoesNotExist:
        logger.warning(f"Closure not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Closure with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def edit_box(request, pk):
    """
    Display and process the form for editing a box.
    
    Handles both GET requests to display the form and POST requests to update
    a box record. Validates input.

    Args:
        request: The HTTP request object
        pk: ID of the box to edit

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to box detail
        On invalid POST: Rendered form template with errors
    """
    try:
        box = get_object_or_404(Box, pk=pk)
        
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=box)
            if form.is_valid():
                box = form.save()
                
                logger.info("Box updated", extra={
                    'user': request.user.username,
                    'box_id': box.id,
                    'box_name': box.name
                })
                
                messages.success(request, 'Box updated successfully.')
                return redirect('packaging:box_detail', pk=box.pk)
            else:
                return render(request, 'packaging/box_form.html', {
                    'form': form,
                    'title': f'Edit Box: {box.name}'
                }, status=400)
        else:
            form = BoxForm(instance=box)
            
        return render(request, 'packaging/box_form.html', {
            'form': form,
            'title': f'Edit Box: {box.name}'
        })
    except Box.DoesNotExist:
        logger.warning(f"Box not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Box with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

# Label Views
@login_required
@handle_view_exception
def list_labels(request):
    """
    Display a list of all labels with search and filter functionality.
    
    Shows labels with their key information including name, stock, and minimum stock.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - labels: QuerySet of filtered labels
        - low_stock: QuerySet of labels with low stock
        - title: Page title
    """
    try:
        labels = Label.objects.all()
        low_stock = labels.filter(stock__lte=F('minimum_stock'))
        context = {
            'labels': labels,
            'low_stock': low_stock,
            'title': 'Labels'
        }
        return render(request, 'packaging/list_labels.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def label_detail(request, pk):
    """
    Display detailed information about a specific label.
    
    Shows all label information including name, stock, and minimum stock.

    Args:
        request: The HTTP request object
        pk: ID of the label to display

    Returns:
        Rendered template with detailed label information
    """
    try:
        label = get_object_or_404(Label, pk=pk)
        context = {
            'label': label,
            'title': f'Label: {label.name}'
        }
        return render(request, 'packaging/label_detail.html', context)
    except Label.DoesNotExist:
        logger.warning(f"Label not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Label with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def add_label(request):
    """
    Display and process the form for adding a new label.
    
    Handles both GET requests to display the form and POST requests to create
    a new label record. Validates input.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to label list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = LabelForm(request.POST, request.FILES)
            if form.is_valid():
                label = form.save(commit=False)
                label.created_by = request.user
                label.save()
                
                logger.info("New label created", extra={
                    'user': request.user.username,
                    'label_id': label.id,
                    'label_name': label.name
                })
                
                messages.success(request, 'Label added successfully.')
                return redirect('packaging:label_detail', pk=label.id)
            else:
                logger.warning("Label creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
        else:
            form = LabelForm()
            
        return render(request, 'packaging/label_form.html', {
            'form': form,
            'title': 'Add New Label'
        })
    except Exception as e:
        log_error(e, request)
        raise

# Closure Views
@login_required
@handle_view_exception
def list_closures(request):
    """
    Display a list of all closures with search and filter functionality.
    
    Shows closures with their key information including name, stock, and minimum stock.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - closures: QuerySet of filtered closures
        - low_stock: QuerySet of closures with low stock
        - title: Page title
    """
    try:
        closures = Closure.objects.all()
        low_stock = closures.filter(stock__lte=F('minimum_stock'))
        context = {
            'closures': closures,
            'low_stock': low_stock,
            'title': 'Closures'
        }
        return render(request, 'packaging/list_closures.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def closure_detail(request, pk):
    """
    Display detailed information about a specific closure.
    
    Shows all closure information including name, stock, and minimum stock.

    Args:
        request: The HTTP request object
        pk: ID of the closure to display

    Returns:
        Rendered template with detailed closure information
    """
    try:
        closure = get_object_or_404(Closure, pk=pk)
        context = {
            'closure': closure,
            'title': f'Closure: {closure.name}'
        }
        return render(request, 'packaging/closure_detail.html', context)
    except Closure.DoesNotExist:
        logger.warning(f"Closure not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Closure with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def add_closure(request):
    """
    Display and process the form for adding a new closure.
    
    Handles both GET requests to display the form and POST requests to create
    a new closure record. Validates input.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to closure list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = ClosureForm(request.POST)
            if form.is_valid():
                closure = form.save(commit=False)
                closure.created_by = request.user
                closure.save()
                
                logger.info("New closure created", extra={
                    'user': request.user.username,
                    'closure_id': closure.id,
                    'closure_name': closure.name
                })
                
                messages.success(request, 'Closure added successfully.')
                return redirect('packaging:closure_detail', pk=closure.id)
            else:
                logger.warning("Closure creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
        else:
            form = ClosureForm()
            
        return render(request, 'packaging/closure_form.html', {
            'form': form,
            'title': 'Add New Closure'
        })
    except Exception as e:
        log_error(e, request)
        raise

# Box Views
@login_required
@handle_view_exception
def list_boxes(request):
    """
    Display a list of all boxes with search and filter functionality.
    
    Shows boxes with their key information including name, stock, and minimum stock.
    Provides search functionality across multiple fields.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - boxes: QuerySet of filtered boxes
        - low_stock: QuerySet of boxes with low stock
        - title: Page title
    """
    try:
        boxes = Box.objects.all()
        low_stock = boxes.filter(stock__lte=F('minimum_stock'))
        context = {
            'boxes': boxes,
            'low_stock': low_stock,
            'title': 'Boxes'
        }
        return render(request, 'packaging/list_boxes.html', context)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def box_detail(request, pk):
    """
    Display detailed information about a specific box.
    
    Shows all box information including name, stock, and minimum stock.

    Args:
        request: The HTTP request object
        pk: ID of the box to display

    Returns:
        Rendered template with detailed box information
    """
    try:
        box = get_object_or_404(Box, pk=pk)
        context = {
            'box': box,
            'title': f'Box: {box.name}'
        }
        return render(request, 'packaging/box_detail.html', context)
    except Box.DoesNotExist:
        logger.warning(f"Box not found: {pk}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Box with id {pk} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def add_box(request):
    """
    Display and process the form for adding a new box.
    
    Handles both GET requests to display the form and POST requests to create
    a new box record. Validates input.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to box list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = BoxForm(request.POST)
            if form.is_valid():
                # Additional validation for bottle capacity
                bottle_capacity = form.cleaned_data['bottle_capacity']
                if bottle_capacity <= 0:
                    return render(request, 'packaging/box_form.html', {
                        'form': form,
                        'title': 'Add New Box',
                        'error': 'Bottle capacity must be greater than 0'
                    }, status=400)
                
                box = form.save(commit=False)
                box.created_by = request.user
                box.save()
                
                logger.info("New box created", extra={
                    'user': request.user.username,
                    'box_id': box.id,
                    'box_name': box.name
                })
                
                messages.success(request, 'Box added successfully.')
                return redirect('packaging:box_detail', pk=box.id)
            else:
                logger.warning("Box creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
                return render(request, 'packaging/box_form.html', {
                    'form': form,
                    'title': 'Add New Box'
                }, status=400)
        else:
            form = BoxForm()
            
        return render(request, 'packaging/box_form.html', {
            'form': form,
            'title': 'Add New Box'
        })
    except Exception as e:
        log_error(e, request)
        raise

# Bottling Views
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
def bottling_detail(request, pk):
    """
    Display detailed information about a specific bottling.
    
    Shows all bottling information including date, bottle, and quantity.

    Args:
        request: The HTTP request object
        pk: ID of the bottling to display

    Returns:
        Rendered template with detailed bottling information
    """
    try:
        bottling = get_object_or_404(Bottling, pk=pk)
        context = {
            'bottling': bottling,
            'title': f'Bottling Details: {bottling.bottle.name}'
        }
        return render(request, 'packaging/bottling_detail.html', context)
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

class BottlingCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new bottling.
    
    Handles both GET requests to display the form and POST requests to create
    a new bottling record. Validates input and updates inventory.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to bottling list
        On invalid POST: Rendered form template with errors
    """
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:list_unfinished')

    def form_valid(self, form):
        """
        Validate the form and update inventory.
        
        Args:
            form: The form instance

        Returns:
            The response object
        """
        try:
            bottling = form.save(commit=False)
            
            # Check if we have enough inventory
            if bottling.quantity > bottling.bottle.stock:
                form.add_error('quantity', 'Not enough bottles in stock')
                return self.form_invalid(form)
                
            if bottling.label and bottling.quantity > bottling.label.stock:
                form.add_error('quantity', 'Not enough labels in stock')
                return self.form_invalid(form)
                
            if bottling.closure and bottling.quantity > bottling.closure.stock:
                form.add_error('quantity', 'Not enough closures in stock')
                return self.form_invalid(form)
                
            if bottling.box:
                boxes_needed = (bottling.quantity + bottling.box.bottle_capacity - 1) // bottling.box.bottle_capacity
                if boxes_needed > bottling.box.stock:
                    form.add_error('quantity', 'Not enough boxes in stock')
                    return self.form_invalid(form)
            
            bottling.created_by = self.request.user
            bottling.save()
            
            # Update inventory
            bottling.bottle.stock -= bottling.quantity
            bottling.bottle.save()
            
            if bottling.label:
                bottling.label.stock -= bottling.quantity
                bottling.label.save()
                
            if bottling.closure:
                bottling.closure.stock -= bottling.quantity
                bottling.closure.save()
                
            if bottling.box:
                bottling.box.stock -= boxes_needed
                bottling.box.save()
            
            messages.success(self.request, 'Bottling created successfully.')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error("Error creating bottling", exc_info=True, extra={
                'user': self.request.user.username
            })
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Return a 400 status code for invalid forms."""
        return self.render_to_response(self.get_context_data(form=form), status=400)

class BottlingUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing bottling.
    
    Handles both GET requests to display the form and POST requests to update
    a bottling record. Validates input and updates inventory.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to bottling list
        On invalid POST: Rendered form template with errors
    """
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:list_unfinished')

    def form_valid(self, form):
        """
        Validate the form and update inventory.
        
        Args:
            form: The form instance

        Returns:
            The response object
        """
        try:
            bottling = form.save(commit=False)
            old_bottling = Bottling.objects.get(pk=bottling.pk)

            # Check if we have enough inventory for the new quantity
            if bottling.quantity > old_bottling.quantity:
                additional_quantity = bottling.quantity - old_bottling.quantity

                # Check bottle inventory
                if bottling.bottle.stock < additional_quantity:
                    form.add_error('quantity', f'Not enough bottles in stock. Available: {bottling.bottle.stock}')
                    return self.form_invalid(form)

                # Check label inventory
                if bottling.label and bottling.label.stock < additional_quantity:
                    form.add_error('quantity', f'Not enough labels in stock. Available: {bottling.label.stock}')
                    return self.form_invalid(form)

                # Check closure inventory
                if bottling.closure and bottling.closure.stock < additional_quantity:
                    form.add_error('quantity', f'Not enough closures in stock. Available: {bottling.closure.stock}')
                    return self.form_invalid(form)

                # Check box inventory
                if bottling.box:
                    boxes_needed = math.ceil(additional_quantity / bottling.box.bottle_capacity)
                    if bottling.box.stock < boxes_needed:
                        form.add_error('quantity', f'Not enough boxes in stock. Available: {bottling.box.stock}')
                        return self.form_invalid(form)

            # Update inventory
            if bottling.quantity != old_bottling.quantity:
                quantity_diff = bottling.quantity - old_bottling.quantity

                # Update bottle stock
                bottling.bottle.stock -= quantity_diff
                bottling.bottle.save()

                # Update label stock
                if bottling.label:
                    bottling.label.stock -= quantity_diff
                    bottling.label.save()

                # Update closure stock
                if bottling.closure:
                    bottling.closure.stock -= quantity_diff
                    bottling.closure.save()

                # Update box stock
                if bottling.box:
                    new_boxes = math.ceil(bottling.quantity / bottling.box.bottle_capacity)
                    old_boxes = math.ceil(old_bottling.quantity / old_bottling.box.bottle_capacity)
                    boxes_diff = new_boxes - old_boxes
                    bottling.box.stock -= boxes_diff
                    bottling.box.save()

            bottling.save()
            return redirect(self.success_url)
        except Exception as e:
            log_error(e, self.request)
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Return a 400 status code for invalid forms."""
        return render(
            self.request,
            self.template_name,
            {'form': form, 'title': f'Edit Bottling: {form.instance.bottle.name}'},
            status=400
        )
