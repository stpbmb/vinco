from django import forms
from .models import Vineyard, Supplier
from cellars.models import Cellar, Tank

class VineyardForm(forms.ModelForm):
    class Meta:
        model = Vineyard
        fields = ['name', 'location', 'size', 'grape_variety', 'ownership_type', 'supplier',
                 'notes', 'arkod_id', 'planting_year', 'cadastral_parcel', 'cadastral_county']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-control supplier-field',
            }),
            'ownership_type': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].required = False
        
        # Initialize supplier visibility based on ownership type
        if self.instance.pk:
            if self.instance.ownership_type != 'supplied':
                self.fields['supplier'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        ownership_type = cleaned_data.get('ownership_type')
        supplier = cleaned_data.get('supplier')

        if ownership_type == 'supplied' and not supplier:
            self.add_error('supplier', 'Supplier is required for supplied vineyards.')
        elif ownership_type == 'owned' and supplier:
            cleaned_data['supplier'] = None

        return cleaned_data

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'oib', 'ibk', 'mibpg']

class CellarForm(forms.ModelForm):
    class Meta:
        model = Cellar
        fields = ['name', 'location', 'capacity', 'notes']

class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = ['name', 'tank_type', 'capacity', 'notes']

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
                raise forms.ValidationError("Source and destination tanks must be different")
            
            if volume > source_tank.current_volume:
                raise forms.ValidationError(
                    f"Transfer volume ({volume}L) exceeds available volume in source tank ({source_tank.current_volume}L)"
                )
            
            available_space = destination_tank.capacity - destination_tank.current_volume
            if volume > available_space:
                raise forms.ValidationError(
                    f"Transfer volume ({volume}L) exceeds available space in destination tank ({available_space}L)"
                )

        return cleaned_data
