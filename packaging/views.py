from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Bottle, Label, Closure, Box, Bottling
from .forms import BottleForm, LabelForm, ClosureForm, BoxForm, BottlingForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from cellars.models import Tank

# Bottle Views
@login_required
def list_bottles(request):
    bottles = Bottle.objects.all()
    low_stock = bottles.filter(stock__lte=F('minimum_stock'))
    context = {
        'bottles': bottles,
        'low_stock': low_stock,
        'title': 'Bottles'
    }
    return render(request, 'packaging/list_bottles.html', context)

@login_required
def bottle_detail(request, pk):
    bottle = get_object_or_404(Bottle, pk=pk)
    context = {
        'bottle': bottle,
        'title': f'Bottle: {bottle.name}'
    }
    return render(request, 'packaging/bottle_detail.html', context)

@login_required
def add_bottle(request):
    if request.method == 'POST':
        form = BottleForm(request.POST)
        if form.is_valid():
            bottle = form.save(commit=False)
            bottle.created_by = request.user
            bottle.save()
            messages.success(request, 'Bottle added successfully.')
            return redirect('packaging:list_bottles')
    else:
        form = BottleForm()
    
    context = {
        'form': form,
        'title': 'Add Bottle'
    }
    return render(request, 'packaging/bottle_form.html', context)

@login_required
def edit_bottle(request, pk):
    bottle = get_object_or_404(Bottle, pk=pk)
    if request.method == 'POST':
        form = BottleForm(request.POST, instance=bottle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bottle updated successfully.')
            return redirect('packaging:bottle_detail', pk=bottle.pk)
    else:
        form = BottleForm(instance=bottle)
    
    context = {
        'form': form,
        'bottle': bottle,
        'title': f'Edit Bottle: {bottle.name}'
    }
    return render(request, 'packaging/bottle_form.html', context)

# Label Views
@login_required
def list_labels(request):
    labels = Label.objects.all()
    low_stock = labels.filter(stock__lte=F('minimum_stock'))
    context = {
        'labels': labels,
        'low_stock': low_stock,
        'title': 'Labels'
    }
    return render(request, 'packaging/list_labels.html', context)

@login_required
def label_detail(request, pk):
    label = get_object_or_404(Label, pk=pk)
    context = {
        'label': label,
        'title': f'Label: {label.name}'
    }
    return render(request, 'packaging/label_detail.html', context)

@login_required
def add_label(request):
    if request.method == 'POST':
        form = LabelForm(request.POST, request.FILES)
        if form.is_valid():
            label = form.save(commit=False)
            label.created_by = request.user
            label.save()
            messages.success(request, 'Label added successfully.')
            return redirect('packaging:list_labels')
    else:
        form = LabelForm()
    
    context = {
        'form': form,
        'title': 'Add Label'
    }
    return render(request, 'packaging/label_form.html', context)

@login_required
def edit_label(request, pk):
    label = get_object_or_404(Label, pk=pk)
    if request.method == 'POST':
        form = LabelForm(request.POST, request.FILES, instance=label)
        if form.is_valid():
            form.save()
            messages.success(request, 'Label updated successfully.')
            return redirect('packaging:label_detail', pk=label.pk)
    else:
        form = LabelForm(instance=label)
    
    context = {
        'form': form,
        'label': label,
        'title': f'Edit Label: {label.name}'
    }
    return render(request, 'packaging/label_form.html', context)

# Closure Views
@login_required
def list_closures(request):
    closures = Closure.objects.all()
    low_stock = closures.filter(stock__lte=F('minimum_stock'))
    context = {
        'closures': closures,
        'low_stock': low_stock,
        'title': 'Closures'
    }
    return render(request, 'packaging/list_closures.html', context)

@login_required
def closure_detail(request, pk):
    closure = get_object_or_404(Closure, pk=pk)
    context = {
        'closure': closure,
        'title': f'Closure: {closure.name}'
    }
    return render(request, 'packaging/closure_detail.html', context)

@login_required
def add_closure(request):
    if request.method == 'POST':
        form = ClosureForm(request.POST)
        if form.is_valid():
            closure = form.save(commit=False)
            closure.created_by = request.user
            closure.save()
            messages.success(request, 'Closure added successfully.')
            return redirect('packaging:list_closures')
    else:
        form = ClosureForm()
    
    context = {
        'form': form,
        'title': 'Add Closure'
    }
    return render(request, 'packaging/closure_form.html', context)

@login_required
def edit_closure(request, pk):
    closure = get_object_or_404(Closure, pk=pk)
    if request.method == 'POST':
        form = ClosureForm(request.POST, instance=closure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Closure updated successfully.')
            return redirect('packaging:closure_detail', pk=closure.pk)
    else:
        form = ClosureForm(instance=closure)
    
    context = {
        'form': form,
        'closure': closure,
        'title': f'Edit Closure: {closure.name}'
    }
    return render(request, 'packaging/closure_form.html', context)

# Box Views
@login_required
def list_boxes(request):
    boxes = Box.objects.all()
    low_stock = boxes.filter(stock__lte=F('minimum_stock'))
    context = {
        'boxes': boxes,
        'low_stock': low_stock,
        'title': 'Boxes'
    }
    return render(request, 'packaging/list_boxes.html', context)

@login_required
def box_detail(request, pk):
    box = get_object_or_404(Box, pk=pk)
    context = {
        'box': box,
        'title': f'Box: {box.name}'
    }
    return render(request, 'packaging/box_detail.html', context)

@login_required
def add_box(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            box = form.save(commit=False)
            box.created_by = request.user
            box.save()
            messages.success(request, 'Box added successfully.')
            return redirect('packaging:list_boxes')
    else:
        form = BoxForm()
    
    context = {
        'form': form,
        'title': 'Add Box'
    }
    return render(request, 'packaging/box_form.html', context)

@login_required
def edit_box(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            messages.success(request, 'Box updated successfully.')
            return redirect('packaging:box_detail', pk=box.pk)
    else:
        form = BoxForm(instance=box)
    
    context = {
        'form': form,
        'box': box,
        'title': f'Edit Box: {box.name}'
    }
    return render(request, 'packaging/box_form.html', context)

# Bottling Views
@login_required
def list_unfinished_bottlings(request):
    bottlings = Bottling.objects.filter(status='unfinished')
    context = {
        'bottlings': bottlings,
        'title': 'Unfinished Bottlings'
    }
    return render(request, 'packaging/list_unfinished.html', context)

@login_required
def list_finished_bottlings(request):
    bottlings = Bottling.objects.exclude(
        Q(closure__isnull=True) | Q(label__isnull=True) | Q(box__isnull=True)
    ).order_by('-bottling_date')
    context = {
        'bottlings': bottlings,
        'title': 'Finished Bottlings'
    }
    return render(request, 'packaging/list_finished.html', context)

class BottlingCreateView(LoginRequiredMixin, CreateView):
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:list_unfinished')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Update inventory quantities
        bottle = form.cleaned_data['bottle']
        quantity = form.cleaned_data['quantity']

        # Reduce bottle stock
        bottle.stock -= quantity
        bottle.save()

        # Reduce packaging materials stock if provided
        for material in ['closure', 'label', 'box']:
            item = form.cleaned_data.get(material)
            if item:
                if material == 'box':
                    # Calculate boxes needed (round up)
                    boxes_needed = (quantity + item.bottle_capacity - 1) // item.bottle_capacity
                    item.stock -= boxes_needed
                else:
                    item.stock -= quantity
                item.save()

        messages.success(self.request, 'Bottling created successfully!')
        return response

class BottlingUpdateView(LoginRequiredMixin, UpdateView):
    model = Bottling
    form_class = BottlingForm
    template_name = 'packaging/bottling_form.html'
    success_url = reverse_lazy('packaging:list_unfinished')

    def form_valid(self, form):
        # Get the old instance before it's updated
        old_instance = Bottling.objects.get(pk=self.object.pk)
        
        # Update the instance
        response = super().form_valid(form)
        
        # Update packaging materials stock if changed
        quantity_diff = form.instance.quantity - old_instance.quantity
        
        if quantity_diff != 0:
            # Update bottle stock
            form.instance.bottle.stock -= quantity_diff
            form.instance.bottle.save()
            
            # Update other materials if they're the same as before
            for material in ['closure', 'label', 'box']:
                old_item = getattr(old_instance, material)
                new_item = getattr(form.instance, material)
                
                if old_item and new_item:
                    if old_item.pk == new_item.pk:
                        # Same material, just update quantity
                        if material == 'box':
                            # Calculate box difference
                            old_boxes = (old_instance.quantity + old_item.bottle_capacity - 1) // old_item.bottle_capacity
                            new_boxes = (form.instance.quantity + new_item.bottle_capacity - 1) // new_item.bottle_capacity
                            new_item.stock -= (new_boxes - old_boxes)
                        else:
                            new_item.stock -= quantity_diff
                        new_item.save()
                    else:
                        # Different material
                        if material == 'box':
                            # Return old boxes to stock
                            old_boxes = (old_instance.quantity + old_item.bottle_capacity - 1) // old_item.bottle_capacity
                            old_item.stock += old_boxes
                            # Take new boxes from stock
                            new_boxes = (form.instance.quantity + new_item.bottle_capacity - 1) // new_item.bottle_capacity
                            new_item.stock -= new_boxes
                        else:
                            old_item.stock += old_instance.quantity
                            new_item.stock -= form.instance.quantity
                        old_item.save()
                        new_item.save()
                elif old_item:
                    # Material removed, return to stock
                    if material == 'box':
                        old_boxes = (old_instance.quantity + old_item.bottle_capacity - 1) // old_item.bottle_capacity
                        old_item.stock += old_boxes
                    else:
                        old_item.stock += old_instance.quantity
                    old_item.save()
                elif new_item:
                    # Material added, take from stock
                    if material == 'box':
                        new_boxes = (form.instance.quantity + new_item.bottle_capacity - 1) // new_item.bottle_capacity
                        new_item.stock -= new_boxes
                    else:
                        new_item.stock -= form.instance.quantity
                    new_item.save()
        
        messages.success(self.request, 'Bottling updated successfully!')
        return response
