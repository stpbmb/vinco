from django.db import models
from django.conf import settings

# Create your models here.

class BaseModel(models.Model):
    """Base model with common fields for all models."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        abstract = True


class TenantModel(BaseModel):
    """Base model for all tenant-specific models."""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        null=True,  # Allow null temporarily for migration
        default=None  # Default to None
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # If no organization is set, try to get it from the current user
        if not self.organization and hasattr(self, 'created_by') and self.created_by:
            from organizations.models import OrganizationUser
            org_user = OrganizationUser.objects.filter(
                user=self.created_by,
                is_primary=True
            ).first()
            if org_user:
                self.organization = org_user.organization
        super().save(*args, **kwargs)
