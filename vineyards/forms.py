from django import forms
from .models import Vineyard

class VineyardForm(forms.ModelForm):
    class Meta:
        model = Vineyard
        fields = '__all__'

from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

from django import forms
from .models import Harvest

class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = '__all__'
        widgets = {
            'crushing_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'pressing_notes': forms.Textarea(attrs={'rows': 3}),
        }

from .models import Cellar, Tank

class CellarForm(forms.ModelForm):
    class Meta:
        model = Cellar
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

from .models import CrushedJuiceAllocation

class CrushedJuiceAllocationForm(forms.ModelForm):
    class Meta:
        model = CrushedJuiceAllocation
        fields = '__all__'
        widgets = {
            'allocation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

from django.forms import inlineformset_factory
from .models import Harvest, CrushedJuiceAllocation

# Create an inline formset for CrushedJuiceAllocation
CrushedJuiceAllocationFormSet = inlineformset_factory(
    Harvest,  # Parent model
    CrushedJuiceAllocation,  # Child model
    fields=('tank', 'allocated_volume', 'allocation_date', 'notes'),  # Fields to include
    extra=1,  # Number of empty forms to display
    widgets={
        'allocation_date': forms.DateInput(attrs={'type': 'date'}),
        'notes': forms.Textarea(attrs={'rows': 3}),
    }
)
