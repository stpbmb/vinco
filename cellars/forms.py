from django import forms
from django.core.exceptions import ValidationError
from .models import Cellar, Tank, CrushedJuiceAllocation

class CellarForm(forms.ModelForm):
    class Meta:
        model = Cellar
        fields = ['name', 'location', 'capacity', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity <= 0:
            raise ValidationError("Capacity must be greater than 0")
        return capacity

class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = ['name', 'tank_type', 'capacity', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tank_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity <= 0:
            raise ValidationError("Capacity must be greater than 0")
        return capacity

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, 'instance') and self.instance.pk:
            # If editing an existing tank
            if self.instance.current_volume > cleaned_data.get('capacity', 0):
                raise ValidationError({
                    'capacity': f"Cannot set capacity below current volume ({self.instance.current_volume}L)"
                })
        return cleaned_data

class CrushedJuiceAllocationForm(forms.ModelForm):
    class Meta:
        model = CrushedJuiceAllocation
        fields = ['harvest', 'tank', 'allocated_volume', 'allocation_date', 'notes']
        widgets = {
            'harvest': forms.Select(attrs={'class': 'form-control'}),
            'tank': forms.Select(attrs={'class': 'form-control'}),
            'allocated_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allocation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get('allocated_volume')
        tank = cleaned_data.get('tank')
        harvest = cleaned_data.get('harvest')

        if volume and tank and harvest:
            if volume > harvest.remaining_juice:
                raise ValidationError({
                    'allocated_volume': f'Cannot allocate more than the remaining juice volume ({harvest.remaining_juice}L)'
                })
            if volume > (tank.capacity - tank.current_volume):
                raise ValidationError({
                    'allocated_volume': f'Cannot allocate more than the available tank space ({tank.capacity - tank.current_volume}L)'
                })

        return cleaned_data

class TankTransferForm(forms.Form):
    source_tank = forms.ModelChoiceField(
        queryset=Tank.objects.all(),
        label="From Tank",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination_tank = forms.ModelChoiceField(
        queryset=Tank.objects.all(),
        label="To Tank",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    volume = forms.FloatField(
        label="Volume to Transfer (L)",
        min_value=0.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    transfer_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def clean(self):
        cleaned_data = super().clean()
        source_tank = cleaned_data.get('source_tank')
        destination_tank = cleaned_data.get('destination_tank')
        volume = cleaned_data.get('volume')

        if source_tank and destination_tank and volume:
            if source_tank == destination_tank:
                raise ValidationError("Cannot transfer wine to the same tank")

            if volume > source_tank.current_volume:
                raise ValidationError({
                    'volume': f'Cannot transfer more than the available volume in source tank ({source_tank.current_volume}L)'
                })

            if volume > (destination_tank.capacity - destination_tank.current_volume):
                raise ValidationError({
                    'volume': f'Cannot transfer more than the available space in destination tank ({destination_tank.capacity - destination_tank.current_volume}L)'
                })

        return cleaned_data
