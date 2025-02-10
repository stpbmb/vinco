"""
Models for managing vineyards and suppliers in the wine production system.

This module contains the core models for tracking vineyards and their suppliers. It handles both
owned and supplied vineyards, including their locations, grape varieties, and other essential details
for wine production management.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import TenantModel

class Supplier(TenantModel):
    """
    Represents a grape supplier in the wine production system.
    
    This model tracks information about external grape suppliers, including their contact details
    and business information. It's used to manage relationships with grape providers and link
    them to their supplied vineyards.

    Attributes:
        name (str): Name of the supplier
        address (str): Physical address of the supplier
        oib (str): Croatian tax number
        ibk (str, optional): Croatian wine producer number
        mibpg (str, optional): Croatian farm number
        created_by (User): User who created the supplier record
        created_at (datetime): Timestamp of creation
    """

    name = models.CharField(max_length=100)
    address = models.TextField()
    oib = models.CharField(max_length=11, unique=True, verbose_name="OIB")  # Croatian tax number
    ibk = models.CharField(max_length=20, blank=True, null=True, verbose_name="IBK")  # Croatian wine producer number
    mibpg = models.CharField(max_length=20, blank=True, null=True, verbose_name="MIBPG")  # Croatian farm number
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """Return a string representation of the supplier."""
        return self.name

    class Meta:
        unique_together = ['organization', 'oib']
        ordering = ['name']
        permissions = [
            ("view_all_suppliers", "Can view all suppliers"),
            ("manage_suppliers", "Can manage suppliers"),
            ("export_supplier_data", "Can export supplier data"),
            ("view_supplier_analytics", "Can view supplier analytics"),
        ]
        indexes = [
            models.Index(fields=['name'], name='supplier_name_idx'),
            models.Index(fields=['oib'], name='supplier_oib_idx'),
            models.Index(fields=['created_at'], name='supplier_created_at_idx'),
        ]

class GrapeVariety(TenantModel):
    """
    Represents an official grape variety in the wine production system.
    
    This model stores the official grape variety codes and their corresponding
    system codes used in the existing database. It provides a mapping between
    the internal system codes and official Croatian wine variety codes.

    Attributes:
        code (str): Official variety code (e.g., 'CV036', 'BV073')
        name (str): Official variety name
        type (str): Type of grape (red or white)
        system_code (str): Internal system code used in database (e.g., 'cabernet_sauvignon')
        created_at (datetime): Timestamp of creation
        created_by (User): User who created the record
    """
    
    code = models.CharField(
        max_length=5,
        help_text="Official variety code (e.g., 'CV036')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Official variety name"
    )
    type = models.CharField(
        max_length=10,
        choices=[('red', 'Red'), ('white', 'White')],
        help_text="Type of grape variety"
    )
    system_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Internal system code (e.g., 'cabernet_sauvignon')"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grape_varieties_created'
    )

    class Meta:
        verbose_name = "grape variety"
        verbose_name_plural = "grape varieties"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code'], name='variety_code_idx'),
            models.Index(fields=['system_code'], name='variety_system_code_idx'),
            models.Index(fields=['type'], name='variety_type_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'code'],
                name='unique_variety_code_per_org'
            )
        ]

    def __str__(self):
        """Return a string representation of the grape variety."""
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate the grape variety model."""
        super().clean()
        
        # Ensure code format is valid
        if self.code:
            if not (self.code.startswith('CV') or self.code.startswith('BV')):
                raise ValidationError({
                    'code': 'Code must start with CV (red) or BV (white)'
                })
            
            # Ensure type matches code prefix
            prefix = self.code[:2]
            if prefix == 'CV' and self.type != 'red':
                raise ValidationError({
                    'type': 'CV codes must be red varieties'
                })
            elif prefix == 'BV' and self.type != 'white':
                raise ValidationError({
                    'type': 'BV codes must be white varieties'
                })

class Vineyard(TenantModel):
    """
    Represents a vineyard in the wine production system.
    
    This model tracks both owned and supplied vineyards, including their physical characteristics,
    location details, and ownership information. It serves as a central reference for harvest
    planning and grape sourcing.

    Attributes:
        name (str): The name of the vineyard
        location (str): Physical location of the vineyard
        size (float): Size of the vineyard in hectares
        grape_variety (str): Type of grape grown in the vineyard
        ownership_type (str): Whether the vineyard is owned or supplied
        supplier (Supplier, optional): Reference to the supplier if ownership_type is 'supplied'
        notes (str, optional): Additional notes about the vineyard
        arkod_id (str, optional): Official ARKOD identification number
        planting_year (int, optional): Year when the vineyard was planted
        cadastral_parcel (str, optional): Official cadastral parcel number
        cadastral_county (str, optional): County where the vineyard is registered
        created_by (User): User who created the vineyard record
        created_at (datetime): Timestamp of creation
    """

    OWNERSHIP_CHOICES = [
        ('owned', 'Owned'),
        ('supplied', 'Supplied'),
    ]

    GRAPE_VARIETY_CHOICES = [
        # Red varieties
        ('merlot', 'Merlot'),
        ('cabernet_sauvignon', 'Cabernet Sauvignon'),
        ('syrah', 'Syrah'),
        ('cabernet_franc', 'Cabernet Franc'),
        ('pinot_noir', 'Pinot Noir'),
        ('zweigelt', 'Zweigelt'),
        
        # White varieties
        ('grasevina', 'Graševina'),
        ('chardonnay', 'Chardonnay'),
        ('sauvignon_blanc', 'Sauvignon Blanc'),
        ('muskat', 'Muškat'),
        ('pinot_bijeli', 'Pinot Bijeli'),
        ('pinot_sivi', 'Pinot Sivi'),
        ('rajnski_rizling', 'Rajnski Rizling'),

        
        # Other
        ('other', 'Other (specify in notes)'),
    ]

    # Basic vineyard information
    name = models.CharField(
        max_length=100,
        help_text="Name of the vineyard"
    )
    ownership_type = models.CharField(
        max_length=10,
        choices=OWNERSHIP_CHOICES,
        help_text="Whether the vineyard is owned or supplied"
    )
    
    # Location information
    location = models.CharField(
        max_length=200,
        help_text="Physical location of the vineyard"
    )
    cadastral_county = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Cadastral county where the vineyard is located"
    )
    cadastral_parcel = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Official cadastral parcel number"
    )
    arkod_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="ARKOD identification number"
    )
    
    # Vineyard characteristics
    size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Size in hectares"
    )
    grape_variety = models.CharField(
        max_length=50,
        choices=GRAPE_VARIETY_CHOICES,
        help_text="Primary grape variety grown"
    )
    planting_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year when the vineyard was planted"
    )
    
    # Supplier relationship (only for supplied vineyards)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vineyards',
        help_text="Supplier for this vineyard (if supplied)"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the vineyard"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vineyards_created'
    )
    
    def __str__(self):
        """Return a string representation of the vineyard."""
        variety_display = dict(self.GRAPE_VARIETY_CHOICES).get(self.grape_variety, self.grape_variety)
        return f"{self.name} - {variety_display}"
    
    def clean(self):
        """Validate the vineyard model."""
        super().clean()
        
        # Validate size is positive
        if self.size is not None and self.size <= 0:
            raise ValidationError({
                'size': 'Size must be greater than 0.'
            })
        
        # Validate supplied vineyards have a supplier
        if self.ownership_type == 'supplied' and not self.supplier:
            raise ValidationError({
                'supplier': 'Supplied vineyards must have a supplier.'
            })

    @property
    def variety_code(self):
        """Get the official variety code."""
        try:
            variety = GrapeVariety.objects.get(system_code=self.grape_variety)
            return variety.code
        except GrapeVariety.DoesNotExist:
            return None

    @property
    def variety_type(self):
        """Get the variety type (red/white)."""
        try:
            variety = GrapeVariety.objects.get(system_code=self.grape_variety)
            return variety.type
        except GrapeVariety.DoesNotExist:
            return None

    class Meta:
        unique_together = ['organization', 'arkod_id']
        ordering = ['name']
        permissions = [
            ("view_all_vineyards", "Can view all vineyards"),
            ("manage_vineyards", "Can manage vineyards"),
            ("export_vineyard_data", "Can export vineyard data"),
            ("view_vineyard_analytics", "Can view vineyard analytics"),
        ]
        indexes = [
            models.Index(fields=['name'], name='vineyard_name_idx'),
            models.Index(fields=['location'], name='vineyard_location_idx'),
            models.Index(fields=['grape_variety'], name='vineyard_grape_var_idx'),
            models.Index(fields=['ownership_type'], name='vineyard_ownership_idx'),
            models.Index(fields=['size'], name='vineyard_size_idx'),
            models.Index(fields=['created_at'], name='vineyard_created_at_idx'),
            models.Index(fields=['supplier', 'ownership_type'], name='vineyard_sup_own_idx'),
        ]
        verbose_name = 'Vineyard'
        verbose_name_plural = 'Vineyards'
