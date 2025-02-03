from django.db import models
from django.conf import settings
from core.models import BaseModel

# Create your models here.

class Organization(BaseModel):
    """
    Represents a tenant organization in the system.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    # Organization details
    address = models.TextField()
    tax_number = models.CharField(max_length=20, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class OrganizationUser(BaseModel):
    """
    Links users to organizations with specific roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('member', 'Member'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['organization', 'user']

    def __str__(self):
        return f"{self.user} ({self.get_role_display()}) - {self.organization}"
