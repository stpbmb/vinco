from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Div, HTML, Submit, Button
from .models import Harvest, HarvestAllocation
from cellars.models import Tank
from vineyards.models import Vineyard
from django.utils import timezone

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
                    css_class='form-row'
                ),
                css_class='form-section'
            ),
            Div(
                HTML('<h3 class="form-section-title">Price Information</h3>'),
                Row(
                    Column('price_per_kg', css_class='form-group col-md-4'),
                    Column('vat_per_kg', css_class='form-group col-md-4'),
                    Column(
                        Div(
                            HTML('<label>Total Amount</label>'),
                            HTML('<div id="total-amount" class="form-control-static">0.00 kn</div>'),
                        ),
                        css_class='form-group col-md-4'
                    ),
                    css_class='form-row'
                ),
                css_class='form-section price-section',
                style='display: none;'
            ),
            Div(
                HTML('<h3 class="form-section-title">Additional Information</h3>'),
                'notes',
                css_class='form-section'
            ),
            Div(
                HTML('<h3 class="form-section-title">Crushing/Pressing Details</h3>'),
                Row(
                    Column('crushing_date', css_class='form-group col-md-6'),
                    Column('juice_yield', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                'pressing_notes',
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
        self.fields['price_per_kg'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'class': 'form-control calculate-total'
        })
        self.fields['vat_per_kg'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'max': '100',
            'class': 'form-control calculate-total',
            'placeholder': 'e.g., 25 for 25%'
        })
        self.fields['juice_yield'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'class': 'form-control',
            'placeholder': 'Juice yield in liters'
        })
        self.fields['crushing_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['pressing_notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Notes about the crushing/pressing process'
        })

    class Meta:
        model = Harvest
        fields = ['vineyard', 'date', 'quantity', 'price_per_kg', 'vat_per_kg', 'notes', 'crushing_date', 'juice_yield', 'pressing_notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'crushing_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'pressing_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        vineyard = cleaned_data.get('vineyard')
        price_per_kg = cleaned_data.get('price_per_kg')
        vat_per_kg = cleaned_data.get('vat_per_kg')

        if vineyard and vineyard.ownership_type == 'supplied':
            if not price_per_kg:
                self.add_error('price_per_kg', 'Price per kg is required for supplied vineyards')
            if vat_per_kg is None:  # Only check if it's None, allow 0
                self.add_error('vat_per_kg', 'VAT percentage is required for supplied vineyards')

        return cleaned_data

class HarvestAllocationForm(forms.ModelForm):
    class Meta:
        model = HarvestAllocation
        fields = ['tank', 'allocated_volume', 'allocation_date', 'notes']
        widgets = {
            'allocation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tank': forms.Select(attrs={'class': 'form-control'}),
            'allocated_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.harvest = kwargs.pop('harvest', None)
        super().__init__(*args, **kwargs)
        
        if self.harvest:
            # Get all tanks and filter in Python for those with available space
            all_tanks = Tank.objects.all()
            available_tanks = [tank for tank in all_tanks if tank.available_space > 0]
            self.fields['tank'].queryset = Tank.objects.filter(id__in=[tank.id for tank in available_tanks])
            self.fields['allocated_volume'].help_text = f'Maximum available: {self.harvest.remaining_juice}L'
            self.fields['tank'].help_text = 'Only tanks with available space are shown'
            
            # Set default allocation date to today
            self.fields['allocation_date'].initial = timezone.now().date()

    def clean_allocated_volume(self):
        volume = self.cleaned_data.get('allocated_volume')
        if not volume:
            raise ValidationError("Please specify an allocation volume")
            
        if not self.harvest:
            raise ValidationError("No harvest specified")
        
        if volume > self.harvest.remaining_juice:
            raise ValidationError(f'Cannot allocate more than the remaining juice volume ({self.harvest.remaining_juice}L)')
        
        return volume

    def clean(self):
        cleaned_data = super().clean()
        tank = cleaned_data.get('tank')
        volume = cleaned_data.get('allocated_volume')

        if tank and volume:
            if volume > tank.available_space:
                raise ValidationError({
                    'allocated_volume': f'Cannot allocate more than the available tank space ({tank.available_space}L)'
                })

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.harvest = self.harvest
        if commit:
            instance.save()
        return instance
