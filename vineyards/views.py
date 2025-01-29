from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Vineyard, Supplier
from .forms import VineyardForm, SupplierForm

# Vineyard Views
@login_required
def list_vineyards(request):
    search_query = request.GET.get('search', '').strip()
    
    owned_vineyards = Vineyard.objects.filter(ownership_type='owned')
    supplied_vineyards = Vineyard.objects.filter(ownership_type='supplied')
    
    if search_query:
        owned_vineyards = owned_vineyards.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(grape_variety__icontains=search_query) |
            Q(cadastral_county__icontains=search_query) |
            Q(arkod_id__icontains=search_query)
        )
        supplied_vineyards = supplied_vineyards.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(grape_variety__icontains=search_query) |
            Q(cadastral_county__icontains=search_query) |
            Q(arkod_id__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    owned_vineyards = owned_vineyards.order_by('name')
    supplied_vineyards = supplied_vineyards.order_by('name')
    
    return render(request, 'vineyards/list_vineyards.html', {
        'owned_vineyards': owned_vineyards,
        'supplied_vineyards': supplied_vineyards,
        'search_query': search_query,
        'active_tab': 'vineyards'
    })

@login_required
def add_vineyard(request):
    if request.method == 'POST':
        form = VineyardForm(request.POST)
        if form.is_valid():
            vineyard = form.save(commit=False)
            vineyard.created_by = request.user
            vineyard.save()
            return redirect('vineyards:vineyard_detail', vineyard_id=vineyard.id)
    else:
        form = VineyardForm()
    return render(request, 'vineyards/vineyard_form.html', {
        'form': form, 
        'title': 'Add New Vineyard',
        'active_tab': 'vineyards'
    })

@login_required
def edit_vineyard(request, vineyard_id):
    vineyard = get_object_or_404(Vineyard, id=vineyard_id)
    if request.method == 'POST':
        form = VineyardForm(request.POST, instance=vineyard)
        if form.is_valid():
            vineyard = form.save()
            return redirect('vineyards:vineyard_detail', vineyard_id=vineyard.id)
    else:
        form = VineyardForm(instance=vineyard)
    return render(request, 'vineyards/vineyard_form.html', {
        'form': form, 
        'title': 'Edit Vineyard',
        'active_tab': 'vineyards'
    })

@login_required
def vineyard_detail(request, vineyard_id):
    vineyard = get_object_or_404(Vineyard, id=vineyard_id)
    return render(request, 'vineyards/vineyard_detail.html', {
        'vineyard': vineyard,
        'active_tab': 'vineyards'
    })

@login_required
def delete_vineyard(request, vineyard_id):
    vineyard = get_object_or_404(Vineyard, id=vineyard_id)
    
    if request.method == 'POST':
        vineyard.delete()
        return redirect('vineyards:list_vineyards')
    
    return render(request, 'vineyards/delete_vineyard.html', {
        'vineyard': vineyard,
        'active_tab': 'vineyards'
    })

# Supplier Views
@login_required
def list_suppliers(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'vineyards/list_suppliers.html', {
        'suppliers': suppliers,
        'active_tab': 'vineyards'
    })

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            return redirect('vineyards:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm()
    return render(request, 'vineyards/supplier_form.html', {
        'form': form, 
        'title': 'Add New Supplier',
        'active_tab': 'vineyards'
    })

@login_required
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            return redirect('vineyards:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'vineyards/supplier_form.html', {
        'form': form, 
        'title': 'Edit Supplier',
        'active_tab': 'vineyards'
    })

@login_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(
        Supplier.objects.prefetch_related('vineyards'),
        id=supplier_id
    )
    return render(request, 'vineyards/supplier_detail.html', {
        'supplier': supplier,
        'active_tab': 'vineyards'
    })
