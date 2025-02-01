from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from .models import Vineyard, Supplier
from cellars.models import Cellar, Tank

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
    
    grape_variety = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-\']+$',
                message='Grape variety can only contain letters, spaces, hyphens, and apostrophes'
            )
        ]
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
        super().__init__(*args, **kwargs)
        self.fields['supplier'].required = False
        
        # Initialize supplier visibility based on ownership type
        if self.instance.pk:
            if self.instance.ownership_type != 'supplied':
                self.fields['supplier'].widget = forms.HiddenInput()

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
    
    contact_name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-\']+$',
                message='Contact name can only contain letters, spaces, hyphens, and apostrophes'
            )
        ]
    )
    
    email = forms.EmailField(
        max_length=254,
        error_messages={
            'invalid': 'Please enter a valid email address'
        }
    )
    
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
            )
        ]
    )
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_name', 'email', 'phone', 'oib', 'ibk', 'mibpg']

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
