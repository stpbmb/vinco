from django import forms
from .models import Harvest, HarvestAllocation
from cellars.models import Tank

class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ['vineyard', 'date', 'quantity', 'notes', 'crushing_date', 'juice_yield', 'pressing_notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'crushing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vineyard': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'juice_yield': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pressing_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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

    def __init__(self, harvest=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if harvest:
            # Get all tanks and filter in Python for those with available space
            all_tanks = Tank.objects.all()
            available_tanks = [tank for tank in all_tanks if tank.available_space > 0]
            self.fields['tank'].queryset = Tank.objects.filter(id__in=[tank.id for tank in available_tanks])
            self.fields['allocated_volume'].help_text = f'Maximum available: {harvest.remaining_juice}L'
            self.fields['tank'].help_text = 'Only tanks with available space are shown'
            self.harvest = harvest

    def clean_allocated_volume(self):
        volume = self.cleaned_data['allocated_volume']
        if hasattr(self, 'harvest') and volume > self.harvest.remaining_juice:
            raise forms.ValidationError(f'Cannot allocate more than the remaining juice volume ({self.harvest.remaining_juice}L)')
        return volume

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get('allocated_volume')
        tank = cleaned_data.get('tank')
        
        if volume and tank and volume > tank.available_space:
            self.add_error('allocated_volume', f'Cannot allocate more than the available tank space ({tank.available_space}L)')
        
        return cleaned_data
