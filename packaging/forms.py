from django import forms
from .models import Bottle, Label, Closure, Box, Bottling
from cellars.models import Tank

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

class BottlingForm(forms.ModelForm):
    class Meta:
        model = Bottling
        fields = ['tank', 'bottle', 'closure', 'label', 'box', 'bottling_date', 'quantity', 'notes']
        widgets = {
            'bottling_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = 'form-control'
        
        # Only show tanks that have wine
        self.fields['tank'].queryset = Tank.objects.filter(current_volume__gt=0)
        
        # Filter out packaging materials that are out of stock
        self.fields['bottle'].queryset = Bottle.objects.filter(stock__gt=0)
        self.fields['closure'].queryset = Closure.objects.filter(stock__gt=0)
        self.fields['label'].queryset = Label.objects.filter(stock__gt=0)
        self.fields['box'].queryset = Box.objects.filter(stock__gt=0)

        # Make packaging materials optional
        self.fields['closure'].required = False
        self.fields['label'].required = False
        self.fields['box'].required = False

        # Add help text
        self.fields['tank'].help_text = 'Select a tank containing wine'
        self.fields['quantity'].help_text = 'Number of bottles to fill'
        self.fields['notes'].help_text = 'Optional notes about the bottling process'

    def clean(self):
        cleaned_data = super().clean()
        tank = cleaned_data.get('tank')
        quantity = cleaned_data.get('quantity')
        bottle = cleaned_data.get('bottle')

        if tank and quantity and bottle:
            # Check if there's enough wine in the tank (convert ml to L)
            required_volume = (quantity * bottle.volume) / 1000  # Convert ml to L
            if required_volume > tank.current_volume:
                raise forms.ValidationError(
                    f'Not enough wine in tank. Need {required_volume}L but only {tank.current_volume}L available.'
                )

            # Check if there are enough bottles in stock
            if quantity > bottle.stock:
                raise forms.ValidationError(
                    f'Not enough bottles in stock. Need {quantity} but only {bottle.stock} available.'
                )

            # Check packaging materials if status would be finished
            closure = cleaned_data.get('closure')
            label = cleaned_data.get('label')
            box = cleaned_data.get('box')

            if all([closure, label, box]):
                # Check closure stock
                if quantity > closure.stock:
                    raise forms.ValidationError(
                        f'Not enough closures in stock. Need {quantity} but only {closure.stock} available.'
                    )
                # Check label stock
                if quantity > label.stock:
                    raise forms.ValidationError(
                        f'Not enough labels in stock. Need {quantity} but only {label.stock} available.'
                    )
                # Check box stock and capacity
                boxes_needed = (quantity + box.bottle_capacity - 1) // box.bottle_capacity  # Round up division
                if boxes_needed > box.stock:
                    raise forms.ValidationError(
                        f'Not enough boxes in stock. Need {boxes_needed} but only {box.stock} available.'
                    )

        return cleaned_data
