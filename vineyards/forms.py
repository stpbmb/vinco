from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from .models import Vineyard, Supplier, GrapeVariety
from cellars.models import Cellar, Tank

class GrapeVarietyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """Display the official name and code of the grape variety."""
        return f"{obj.name} ({obj.code})"
    
    def to_python(self, value):
        """Convert the selected GrapeVariety to its system_code."""
        if value in self.empty_values:
            return None
        try:
            value = super().to_python(value)
            return value.system_code
        except (ValueError, TypeError):
            return value

class VineyardForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\']+$',
                message='Name can only contain letters, numbers, spaces, hyphens, and apostrophes'
            )
        ]
    )
    
    location = forms.CharField(
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\',\.]+$',
                message='Location can only contain letters, numbers, spaces, hyphens, commas, periods, and apostrophes'
            )
        ]
    )
    
    grape_variety = GrapeVarietyChoiceField(
        queryset=GrapeVariety.objects.none(),
        label="Grape Variety",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-wine-500 focus:ring-wine-500 sm:text-sm'
        })
    )
    
    size = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message='Size must be greater than 0'),
            MaxValueValidator(10000, message='Size cannot exceed 10,000 hectares')
        ]
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Set up grape variety choices filtered by organization
        if organization:
            self.fields['grape_variety'].queryset = GrapeVariety.objects.filter(
                organization=organization
            ).order_by('type', 'name')
        
        # Set initial grape variety based on system_code if editing
        if self.instance and self.instance.pk and self.instance.grape_variety:
            try:
                variety = GrapeVariety.objects.get(
                    organization=organization,
                    system_code=self.instance.grape_variety
                )
                self.fields['grape_variety'].initial = variety
            except GrapeVariety.DoesNotExist:
                pass
        
        self.fields['supplier'].required = False
        
        # Initialize supplier visibility based on ownership type
        if self.instance.pk:
            if self.instance.ownership_type != 'supplied':
                self.fields['supplier'].widget = forms.HiddenInput()

    def clean_planting_year(self):
        """Clean the planting_year field to handle empty values."""
        planting_year = self.cleaned_data.get('planting_year')
        if planting_year == '':
            return None
        return planting_year

    def clean(self):
        cleaned_data = super().clean()
        
        # Additional cross-field validation
        ownership_type = cleaned_data.get('ownership_type')
        supplier = cleaned_data.get('supplier')
        
        if ownership_type == 'supplied' and not supplier:
            raise forms.ValidationError({
                'supplier': 'Supplier is required for supplied vineyards'
            })
        
        if ownership_type == 'owned' and supplier:
            raise forms.ValidationError({
                'supplier': 'Owned vineyards should not have a supplier'
            })
        
        return cleaned_data
    
    class Meta:
        model = Vineyard
        fields = ['name', 'location', 'size', 'grape_variety', 'ownership_type', 'supplier', 'notes', 'arkod_id', 'planting_year', 'cadastral_parcel', 'cadastral_county']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-control supplier-field',
            }),
            'ownership_type': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

class SupplierForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\']+$',
                message='Name can only contain letters, numbers, spaces, hyphens, and apostrophes'
            )
        ]
    )
    
    address = forms.CharField(
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\',\.]+$',
                message='Address can only contain letters, numbers, spaces, hyphens, commas, periods, and apostrophes'
            )
        ]
    )
    
    oib = forms.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='OIB must be exactly 11 digits'
            )
        ]
    )
    
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'oib']

class CellarForm(forms.ModelForm):
    class Meta:
        model = Cellar
        fields = ['name', 'location', 'notes']

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
