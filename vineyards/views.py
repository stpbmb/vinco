from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vineyard, Supplier, Harvest, Cellar, Tank, CrushedJuiceAllocation
from .forms import VineyardForm, SupplierForm, HarvestForm, CrushedJuiceAllocationFormSet, CrushedJuiceAllocationForm, CellarForm, TankForm

# Vineyard Views
def list_vineyards(request):
    vineyards = Vineyard.objects.all()
    return render(request, 'vineyards/list_vineyards.html', {'vineyards': vineyards})

def add_vineyard(request):
    if request.method == 'POST':
        form = VineyardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_vineyards')
    else:
        form = VineyardForm()
    return render(request, 'vineyards/add_vineyard.html', {'form': form})

def edit_vineyard(request, vineyard_id):
    vineyard = get_object_or_404(Vineyard, id=vineyard_id)
    if request.method == 'POST':
        form = VineyardForm(request.POST, instance=vineyard)
        if form.is_valid():
            form.save()
            return redirect('list_vineyards')
    else:
        form = VineyardForm(instance=vineyard)
    return render(request, 'vineyards/edit_vineyard.html', {'form': form})

def vineyard_detail(request, vineyard_id):
    vineyard = get_object_or_404(Vineyard, id=vineyard_id)
    return render(request, 'vineyards/vineyard_detail.html', {'vineyard': vineyard})

# Supplier Views
def list_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'vineyards/list_suppliers.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_suppliers')
    else:
        form = SupplierForm()
    return render(request, 'vineyards/add_supplier.html', {'form': form})

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('list_suppliers')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'vineyards/edit_supplier.html', {'form': form})

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    return render(request, 'vineyards/supplier_detail.html', {'supplier': supplier})

# Harvest Views
@login_required
def list_harvests(request):
    harvests = Harvest.objects.all()
    return render(request, 'vineyards/list_harvests.html', {'harvests': harvests})

@login_required
def add_harvest(request):
    if request.method == 'POST':
        form = HarvestForm(request.POST)
        formset = CrushedJuiceAllocationFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            harvest = form.save(commit=False)
            harvest.created_by = request.user
            harvest.save()
            allocations = formset.save(commit=False)
            for allocation in allocations:
                allocation.harvest = harvest
                allocation.save()
                allocation.tank.update_volume(allocation.allocated_volume)
            return redirect('list_harvests')
    else:
        form = HarvestForm()
        formset = CrushedJuiceAllocationFormSet()
    return render(request, 'vineyards/add_harvest.html', {
        'form': form,
        'formset': formset,
    })

@login_required
def edit_harvest(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    if request.method == 'POST':
        form = HarvestForm(request.POST, instance=harvest)
        if form.is_valid():
            form.save()
            return redirect('list_harvests')
    else:
        form = HarvestForm(instance=harvest)
    return render(request, 'vineyards/edit_harvest.html', {'form': form})

@login_required
def harvest_detail(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    allocations = harvest.allocations.all()
    if request.method == 'POST':
        form = CrushedJuiceAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.harvest = harvest
            allocation.save()
            allocation.tank.update_volume(allocation.allocated_volume)
            return redirect('harvest_detail', harvest_id=harvest.id)
    else:
        form = CrushedJuiceAllocationForm()
    return render(request, 'vineyards/harvest_detail.html', {
        'harvest': harvest,
        'allocations': allocations,
        'form': form,
    })

# Cellar Views
def list_cellars(request):
    cellars = Cellar.objects.all()
    return render(request, 'vineyards/list_cellars.html', {'cellars': cellars})

def add_cellar(request):
    if request.method == 'POST':
        form = CellarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_cellars')
    else:
        form = CellarForm()
    return render(request, 'vineyards/add_cellar.html', {'form': form})

def edit_cellar(request, cellar_id):
    cellar = get_object_or_404(Cellar, id=cellar_id)
    if request.method == 'POST':
        form = CellarForm(request.POST, instance=cellar)
        if form.is_valid():
            form.save()
            return redirect('list_cellars')
    else:
        form = CellarForm(instance=cellar)
    return render(request, 'vineyards/edit_cellar.html', {'form': form})

def cellar_detail(request, cellar_id):
    cellar = get_object_or_404(Cellar, id=cellar_id)
    tanks = cellar.tanks.all()
    return render(request, 'vineyards/cellar_detail.html', {'cellar': cellar, 'tanks': tanks})

# Tank Views
def add_tank(request, cellar_id):
    cellar = get_object_or_404(Cellar, id=cellar_id)
    if request.method == 'POST':
        form = TankForm(request.POST)
        if form.is_valid():
            tank = form.save(commit=False)
            tank.cellar = cellar
            tank.save()
            return redirect('cellar_detail', cellar_id=cellar.id)
    else:
        form = TankForm()
    return render(request, 'vineyards/add_tank.html', {'form': form, 'cellar': cellar})

def edit_tank(request, tank_id):
    tank = get_object_or_404(Tank, id=tank_id)
    if request.method == 'POST':
        form = TankForm(request.POST, instance=tank)
        if form.is_valid():
            form.save()
            return redirect('cellar_detail', cellar_id=tank.cellar.id)
    else:
        form = TankForm(instance=tank)
    return render(request, 'vineyards/edit_tank.html', {'form': form, 'tank': tank})

# Allocation Views
def list_allocations(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    allocations = harvest.allocations.all()
    return render(request, 'vineyards/list_allocations.html', {'harvest': harvest, 'allocations': allocations})

def add_allocation(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    if request.method == 'POST':
        form = CrushedJuiceAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.harvest = harvest
            allocation.save()
            allocation.tank.update_volume(allocation.allocated_volume)
            return redirect('list_allocations', harvest_id=harvest.id)
    else:
        form = CrushedJuiceAllocationForm()
    return render(request, 'vineyards/add_allocation.html', {'form': form, 'harvest': harvest})

def edit_allocation(request, allocation_id):
    allocation = get_object_or_404(CrushedJuiceAllocation, id=allocation_id)
    if request.method == 'POST':
        form = CrushedJuiceAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            # Revert the old volume
            allocation.tank.update_volume(-allocation.allocated_volume)
            # Save the updated allocation
            allocation = form.save()
            # Update the tank's current volume with the new allocation
            allocation.tank.update_volume(allocation.allocated_volume)
            return redirect('list_allocations', harvest_id=allocation.harvest.id)
    else:
        form = CrushedJuiceAllocationForm(instance=allocation)
    return render(request, 'vineyards/edit_allocation.html', {'form': form, 'allocation': allocation})
