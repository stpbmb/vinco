from django import forms

class TenantFormMixin:
    """
    Mixin to handle organization-based filtering in forms.
    """
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        # Filter foreign key fields by organization
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                model = field.queryset.model
                if hasattr(model, 'organization'):
                    field.queryset = field.queryset.filter(organization=self.organization)

    def save(self, commit=True):
        """Set the organization before saving the form."""
        instance = super().save(commit=False)
        if hasattr(instance, 'organization') and not instance.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance
