from django import forms
from .models import Bottle, Label, Closure, Box

class BottleForm(forms.ModelForm):
    class Meta:
        model = Bottle
        fields = [
            'name', 'bottle_type', 'volume', 'glass_color',
            'height', 'diameter', 'weight', 'supplier',
            'price', 'stock', 'minimum_stock', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = [
            'name', 'label_type', 'material', 'width',
            'height', 'supplier', 'price', 'stock',
            'minimum_stock', 'design_file', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ClosureForm(forms.ModelForm):
    class Meta:
        model = Closure
        fields = [
            'name', 'closure_type', 'material', 'color',
            'diameter', 'height', 'supplier', 'price',
            'stock', 'minimum_stock', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = [
            'name', 'box_type', 'material', 'bottle_capacity',
            'length', 'width', 'height', 'weight',
            'supplier', 'price', 'stock', 'minimum_stock',
            'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
