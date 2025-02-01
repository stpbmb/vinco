"""
Views for managing vineyards and suppliers in the wine production system.

This module provides views for listing, creating, updating, and deleting vineyards
and suppliers. It includes functionality for searching and filtering vineyards by
various criteria.
"""

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from vinco.exceptions import (
    handle_view_exception,
    InvalidOperationError,
    ResourceNotFoundError,
    ValidationError,
    log_error
)
from .models import Vineyard, Supplier
from .forms import VineyardForm, SupplierForm
from django.db.models import Q

logger = logging.getLogger('vinco')

# Vineyard Views
@login_required
@permission_required('vineyards.view_vineyard', raise_exception=True)
@handle_view_exception
def list_vineyards(request):
    """
    Display a list of all vineyards with search functionality.
    
    Lists vineyards separated into owned and supplied categories. Provides search
    functionality across multiple fields including name, location, grape variety,
    and supplier information.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with context containing:
        - owned_vineyards: QuerySet of owned vineyards
        - supplied_vineyards: QuerySet of supplied vineyards
        - search_query: Current search term if any
        - active_tab: Current active navigation tab
    """
    try:
        search_query = request.GET.get('search', '').strip()
        
        # Base queryset with optimized joins
        base_qs = Vineyard.objects.select_related('supplier', 'created_by')
        
        # If user doesn't have view_all_vineyards permission, only show their vineyards
        if not request.user.has_perm('vineyards.view_all_vineyards'):
            base_qs = base_qs.filter(created_by=request.user)
        
        # Filter owned vineyards
        owned_vineyards = base_qs.filter(ownership_type='owned')
        
        # Filter supplier vineyards
        supplied_vineyards = base_qs.filter(ownership_type='supplied')
        
        if search_query:
            # Apply search filter to both querysets
            search_filter = (
                Q(name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(grape_variety__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )
            owned_vineyards = owned_vineyards.filter(search_filter)
            supplied_vineyards = supplied_vineyards.filter(search_filter)
        
        # Order the results
        owned_vineyards = owned_vineyards.order_by('name')
        supplied_vineyards = supplied_vineyards.order_by('supplier__name', 'name')
        
        context = {
            'owned_vineyards': owned_vineyards,
            'supplied_vineyards': supplied_vineyards,
            'search_query': search_query,
            'active_tab': 'vineyards',
            'can_manage': request.user.has_perm('vineyards.manage_vineyards'),
            'can_export': request.user.has_perm('vineyards.export_vineyard_data'),
            'can_view_analytics': request.user.has_perm('vineyards.view_vineyard_analytics'),
        }
        
        return render(request, 'vineyards/list_vineyards.html', context)
        
    except Exception as e:
        log_error(logger, e)
        messages.error(request, str(e))
        return redirect('home')

@login_required
@permission_required(['vineyards.add_vineyard', 'vineyards.manage_vineyards'], raise_exception=True)
@handle_view_exception
def add_vineyard(request):
    """
    Display and process the form for adding a new vineyard.
    
    Handles both GET requests to display the form and POST requests to create
    a new vineyard. Associates the created vineyard with the current user.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to vineyard list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = VineyardForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    vineyard = form.save(commit=False)
                    vineyard.created_by = request.user
                    vineyard.save()
                    
                    logger.info("New vineyard created", extra={
                        'user': request.user.username,
                        'vineyard_id': vineyard.id,
                        'vineyard_name': vineyard.name
                    })
                    
                    messages.success(request, 'Vineyard added successfully.')
                    return redirect('vineyards:vineyard_detail', vineyard_id=vineyard.id)
            else:
                logger.warning("Vineyard creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
        else:
            form = VineyardForm()
            
        return render(request, 'vineyards/vineyard_form.html', {
            'form': form,
            'title': 'Add New Vineyard',
            'active_tab': 'vineyards'
        })
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@permission_required(['vineyards.change_vineyard', 'vineyards.manage_vineyards'], raise_exception=True)
@handle_view_exception
def edit_vineyard(request, vineyard_id):
    """
    Display and process the form for editing an existing vineyard.
    
    Handles both GET requests to display the pre-populated form and POST
    requests to update the vineyard.

    Args:
        request: The HTTP request object
        vineyard_id: ID of the vineyard to edit

    Returns:
        On GET: Rendered form template with pre-populated data
        On successful POST: Redirect to vineyard list
        On invalid POST: Rendered form template with errors
    """
    try:
        vineyard = get_object_or_404(Vineyard, id=vineyard_id)
        
        # Check if user has permission to edit this specific vineyard
        if not request.user.has_perm('vineyards.manage_vineyards') and vineyard.created_by != request.user:
            raise PermissionDenied("You don't have permission to edit this vineyard.")
        
        if request.method == 'POST':
            form = VineyardForm(request.POST, instance=vineyard)
            if form.is_valid():
                with transaction.atomic():
                    vineyard = form.save()
                    
                    logger.info("Vineyard updated", extra={
                        'user': request.user.username,
                        'vineyard_id': vineyard.id,
                        'vineyard_name': vineyard.name
                    })
                    
                    messages.success(request, 'Vineyard updated successfully.')
                    return redirect('vineyards:vineyard_detail', vineyard_id=vineyard.id)
            else:
                logger.warning("Vineyard update failed - form validation error", extra={
                    'user': request.user.username,
                    'vineyard_id': vineyard.id,
                    'form_errors': form.errors
                })
        else:
            form = VineyardForm(instance=vineyard)
            
        return render(request, 'vineyards/vineyard_form.html', {
            'form': form,
            'title': 'Edit Vineyard',
            'active_tab': 'vineyards'
        })
    except Vineyard.DoesNotExist:
        logger.warning(f"Vineyard not found: {vineyard_id}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Vineyard with id {vineyard_id} not found")
    except Exception as e:
        log_error(logger, e)
        messages.error(request, str(e))
        return redirect('home')

@login_required
@handle_view_exception
def vineyard_detail(request, vineyard_id):
    """
    Display detailed information about a specific vineyard.
    
    Shows all vineyard information including harvest history and related data.
    Uses select_related and prefetch_related to optimize database queries.

    Args:
        request: The HTTP request object
        vineyard_id: ID of the vineyard to display

    Returns:
        Rendered template with detailed vineyard information
    """
    try:
        # Optimize queries by selecting related fields and prefetching related data
        vineyard = get_object_or_404(
            Vineyard.objects.select_related(
                'supplier',
                'created_by'
            ).prefetch_related(
                'harvests__created_by',
                'harvests__allocations__tank__cellar',
                'harvests__allocations__created_by'
            ),
            id=vineyard_id
        )
        
        context = {
            'vineyard': vineyard,
            'active_tab': 'vineyards'
        }
        
        return render(request, 'vineyards/vineyard_detail.html', context)
        
    except Exception as e:
        log_error(logger, e)
        messages.error(request, str(e))
        return redirect('home')

@login_required
@permission_required(['vineyards.delete_vineyard', 'vineyards.manage_vineyards'], raise_exception=True)
@handle_view_exception
def delete_vineyard(request, vineyard_id):
    """
    Handle vineyard deletion.
    
    Deletes the specified vineyard and redirects to the vineyard list.
    Requires POST request for security.

    Args:
        request: The HTTP request object
        vineyard_id: ID of the vineyard to delete

    Returns:
        On POST: Redirect to vineyard list
        On GET: Rendered confirmation template
    """
    try:
        vineyard = get_object_or_404(Vineyard, id=vineyard_id)
        
        # Check if user has permission to delete this specific vineyard
        if not request.user.has_perm('vineyards.manage_vineyards') and vineyard.created_by != request.user:
            raise PermissionDenied("You don't have permission to delete this vineyard.")
        
        # Check if vineyard has any related harvests
        if vineyard.harvests.exists():
            raise InvalidOperationError(
                "Cannot delete vineyard with existing harvests",
                code='vineyard_has_harvests'
            )
                
        if request.method == 'POST':
            vineyard_name = vineyard.name
            vineyard.delete()
            
            logger.info("Vineyard deleted", extra={
                'user': request.user.username,
                'vineyard_id': vineyard_id,
                'vineyard_name': vineyard_name
            })
            
            messages.success(request, 'Vineyard deleted successfully.')
            return redirect('vineyards:list_vineyards')
            
        return render(request, 'vineyards/delete_vineyard.html', {
            'vineyard': vineyard,
            'active_tab': 'vineyards'
        })
    except Vineyard.DoesNotExist:
        logger.warning(f"Vineyard not found: {vineyard_id}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Vineyard with id {vineyard_id} not found")
    except InvalidOperationError as e:
        logger.warning(str(e), extra={
            'user': request.user.username,
            'vineyard_id': vineyard_id
        })
        messages.error(request, str(e))
        return redirect('vineyards:vineyard_detail', vineyard_id=vineyard_id)
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def vineyard_api(request, vineyard_id):
    """
    Return JSON data for a specific vineyard.
    
    Returns ownership type of the vineyard.

    Args:
        request: The HTTP request object
        vineyard_id: ID of the vineyard

    Returns:
        JSON response with ownership type
    """
    try:
        vineyard = get_object_or_404(Vineyard, id=vineyard_id)
        
        logger.info("Vineyard API accessed", extra={
            'user': request.user.username,
            'vineyard_id': vineyard.id,
            'vineyard_name': vineyard.name
        })
        
        return JsonResponse({
            'ownership_type': vineyard.ownership_type,
        })
    except Vineyard.DoesNotExist:
        logger.warning(f"Vineyard not found: {vineyard_id}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Vineyard with id {vineyard_id} not found")
    except Exception as e:
        log_error(e, request)
        raise

# Supplier Views
@login_required
@handle_view_exception
def list_suppliers(request):
    """
    Display a list of all suppliers.
    
    Lists all suppliers ordered by name.

    Args:
        request: The HTTP request object

    Returns:
        Rendered template with list of suppliers
    """
    try:
        suppliers = Supplier.objects.all().order_by('name')
        
        logger.info("Suppliers list accessed", extra={
            'user': request.user.username
        })
        
        return render(request, 'vineyards/list_suppliers.html', {
            'suppliers': suppliers,
            'active_tab': 'vineyards'
        })
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def add_supplier(request):
    """
    Display and process the form for adding a new supplier.
    
    Handles both GET requests to display the form and POST requests to create
    a new supplier. Associates the created supplier with the current user.

    Args:
        request: The HTTP request object

    Returns:
        On GET: Rendered form template
        On successful POST: Redirect to supplier list
        On invalid POST: Rendered form template with errors
    """
    try:
        if request.method == 'POST':
            form = SupplierForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    supplier = form.save(commit=False)
                    supplier.created_by = request.user
                    supplier.save()
                    
                    logger.info("New supplier created", extra={
                        'user': request.user.username,
                        'supplier_id': supplier.id,
                        'supplier_name': supplier.name
                    })
                    
                    messages.success(request, 'Supplier added successfully.')
                    return redirect('vineyards:supplier_detail', supplier_id=supplier.id)
            else:
                logger.warning("Supplier creation failed - form validation error", extra={
                    'user': request.user.username,
                    'form_errors': form.errors
                })
        else:
            form = SupplierForm()
            
        return render(request, 'vineyards/supplier_form.html', {
            'form': form,
            'title': 'Add New Supplier',
            'active_tab': 'vineyards'
        })
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def edit_supplier(request, supplier_id):
    """
    Display and process the form for editing an existing supplier.
    
    Handles both GET requests to display the pre-populated form and POST
    requests to update the supplier.

    Args:
        request: The HTTP request object
        supplier_id: ID of the supplier to edit

    Returns:
        On GET: Rendered form template with pre-populated data
        On successful POST: Redirect to supplier list
        On invalid POST: Rendered form template with errors
    """
    try:
        supplier = get_object_or_404(Supplier, id=supplier_id)
        
        if request.method == 'POST':
            form = SupplierForm(request.POST, instance=supplier)
            if form.is_valid():
                with transaction.atomic():
                    supplier = form.save()
                    
                    logger.info("Supplier updated", extra={
                        'user': request.user.username,
                        'supplier_id': supplier.id,
                        'supplier_name': supplier.name
                    })
                    
                    messages.success(request, 'Supplier updated successfully.')
                    return redirect('vineyards:supplier_detail', supplier_id=supplier.id)
            else:
                logger.warning("Supplier update failed - form validation error", extra={
                    'user': request.user.username,
                    'supplier_id': supplier.id,
                    'form_errors': form.errors
                })
        else:
            form = SupplierForm(instance=supplier)
            
        return render(request, 'vineyards/supplier_form.html', {
            'form': form,
            'title': 'Edit Supplier',
            'active_tab': 'vineyards'
        })
    except Supplier.DoesNotExist:
        logger.warning(f"Supplier not found: {supplier_id}", extra={
            'user': request.user.username
        })
        raise ResourceNotFoundError(f"Supplier with id {supplier_id} not found")
    except Exception as e:
        log_error(e, request)
        raise

@login_required
@handle_view_exception
def supplier_detail(request, supplier_id):
    """
    Display detailed information about a specific supplier.
    
    Shows all supplier information including associated vineyards.
    Uses select_related and prefetch_related to optimize database queries.

    Args:
        request: The HTTP request object
        supplier_id: ID of the supplier to display

    Returns:
        Rendered template with detailed supplier information
    """
    try:
        # Optimize queries by selecting related fields and prefetching related data
        supplier = get_object_or_404(
            Supplier.objects.prefetch_related(
                'vineyards__created_by',
                'vineyards__harvests__created_by',
                'vineyards__harvests__allocations__tank__cellar'
            ),
            id=supplier_id
        )
        
        context = {
            'supplier': supplier,
            'active_tab': 'suppliers'
        }
        
        return render(request, 'vineyards/supplier_detail.html', context)
        
    except Exception as e:
        log_error(logger, e)
        messages.error(request, str(e))
        return redirect('home')

@login_required
@handle_view_exception
def delete_supplier(request, supplier_id):
    """
    Handle supplier deletion.
    
    Deletes the specified supplier and redirects to the supplier list.
    Requires POST request for security.

    Args:
        request: The HTTP request object
        supplier_id: ID of the supplier to delete

    Returns:
        On POST: Redirect to supplier list
        On GET: Rendered confirmation template
    """
    try:
        supplier = get_object_or_404(Supplier, id=supplier_id)
        
        # Check if supplier has associated vineyards
        if supplier.vineyards.exists():
            raise InvalidOperationError(
                "Cannot delete supplier with associated vineyards. "
                "Please reassign or delete the vineyards first."
            )
        
        if request.method == 'POST':
            supplier_name = supplier.name
            supplier.delete()
            
            messages.success(
                request,
                f'Successfully deleted supplier "{supplier_name}"'
            )
            
            logger.info("Supplier deleted", extra={
                'user': request.user.username,
                'supplier_id': supplier_id,
                'supplier_name': supplier_name
            })
            
            return redirect('vineyards:list_suppliers')
        
        return render(request, 'vineyards/delete_supplier.html', {
            'supplier': supplier,
            'active_tab': 'suppliers'
        })
        
    except InvalidOperationError as e:
        messages.error(request, str(e))
        return redirect('vineyards:supplier_detail', supplier_id=supplier_id)
    except Exception as e:
        log_error(e, request)
        raise
