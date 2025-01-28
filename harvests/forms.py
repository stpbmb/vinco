from django import forms
from django.core.exceptions import ValidationError
from .models import Harvest, HarvestAllocation
from cellars.models import Tank
from django.utils import timezone

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
