from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML, Submit, Button
from .models import Harvest, HarvestAllocation
from cellars.models import Tank
from vineyards.models import Vineyard
from django.utils import timezone
from django.db import models

class HarvestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'harvest-form'
        self.helper.layout = Layout(
            Div(
                HTML('<h3 class="form-section-title">Basic Information</h3>'),
                Row(
                    Column('vineyard', css_class='form-group col-md-6'),
                    Column('date', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                Row(
                    Column('quantity', css_class='form-group col-md-6'),
                    Column('juice_yield', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                css_class='form-section'
            ),
            Div(
                HTML('<h3 class="form-section-title">Additional Information</h3>'),
                'notes',
                css_class='form-section'
            ),
            Div(
                Row(
                    Column(
                        Div(
                            Submit('submit', 'Save Harvest', css_class='btn btn-primary'),
                            HTML('<a href="{% url \'harvests:list_harvests\' %}" class="btn btn-secondary">Cancel</a>'),
                            css_class='form-actions'
                        ),
                        css_class='col-12'
                    ),
                    css_class='form-row'
                ),
                css_class='form-section form-actions-section'
            )
        )
        
        # Add classes to form fields
        self.fields['vineyard'].widget.attrs.update({'class': 'select2'})
        self.fields['date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['quantity'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'class': 'form-control'
        })
        self.fields['juice_yield'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'max': '1',
            'class': 'form-control',
            'placeholder': 'Juice yield (e.g., 0.75 for 75%)'
        })

    class Meta:
        model = Harvest
        fields = ['vineyard', 'date', 'quantity', 'juice_yield', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk:  # Only check if this is an existing harvest being updated
            quantity = cleaned_data.get('quantity')
            juice_yield = cleaned_data.get('juice_yield')
            
            if quantity and juice_yield:
                allocated_volume = self.instance.allocations.aggregate(
                    total=models.Sum('allocated_volume')
                )['total'] or 0
                
                if float(quantity) * float(juice_yield) < float(allocated_volume):
                    raise ValidationError(
                        "Cannot reduce harvest quantity below already allocated volume"
                    )
        return cleaned_data

class HarvestAllocationForm(forms.ModelForm):
    class Meta:
        model = HarvestAllocation
        fields = ['harvest', 'tank', 'allocated_volume', 'allocation_date']
        widgets = {
            'harvest': forms.Select(attrs={'class': 'form-control'}),
            'tank': forms.Select(attrs={'class': 'form-control'}),
            'allocated_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allocation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.harvest = kwargs.pop('harvest', None)
        super().__init__(*args, **kwargs)
        if self.harvest:
            self.fields['harvest'].initial = self.harvest
            self.fields['harvest'].widget = forms.HiddenInput()

    def clean_allocated_volume(self):
        allocated_volume = self.cleaned_data.get('allocated_volume')
        if allocated_volume is None:
            raise ValidationError('Allocated volume is required')
        if allocated_volume <= 0:
            raise ValidationError('Allocated volume must be greater than 0')
        return allocated_volume

    def clean(self):
        cleaned_data = super().clean()
        allocated_volume = cleaned_data.get('allocated_volume')
        tank = cleaned_data.get('tank')
        harvest = cleaned_data.get('harvest') or self.harvest

        if allocated_volume and tank and harvest:
            # Check tank capacity
            available_tank_space = tank.capacity - tank.current_volume
            if allocated_volume > available_tank_space:
                raise ValidationError({
                    'allocated_volume': 'Allocation would exceed tank capacity'
                })

            # Check harvest available juice
            total_juice = harvest.quantity * harvest.juice_yield
            allocated = harvest.allocations.exclude(pk=self.instance.pk if self.instance.pk else None).aggregate(
                total=models.Sum('allocated_volume')
            )['total'] or 0
            available_juice = total_juice - allocated

            if allocated_volume > available_juice:
                raise ValidationError({
                    'allocated_volume': 'Cannot allocate more than available juice'
                })

        return cleaned_data
