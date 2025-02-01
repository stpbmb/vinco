"""
Models for managing grape harvests and juice allocations in the wine production process.

This module contains models for tracking grape harvests from vineyards and managing the allocation
of juice to different tanks. It handles harvest details, pressing information, and juice distribution
throughout the production process.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from vineyards.models import Vineyard

User = get_user_model()

class Harvest(models.Model):
    """
    Represents a grape harvest event in the wine production process.
    
    This model tracks the harvesting of grapes from vineyards, including quantities,
    pricing information for supplied grapes, and juice yield from pressing. It serves
    as the primary record for grape intake and initial processing.

    Attributes:
        vineyard (Vineyard): The vineyard where grapes were harvested
        date (date): Date of the harvest
        quantity (float): Quantity of grapes harvested in kilograms
        notes (str, optional): General notes about the harvest
        price_per_kg (decimal, optional): Price per kilogram for supplied grapes
        vat_per_kg (decimal, optional): VAT percentage for supplied grapes
        crushing_date (date, optional): Date when grapes were crushed/pressed
        juice_yield (float, optional): Amount of juice obtained in liters
        pressing_notes (str, optional): Notes about the crushing/pressing process
        created_by (User): User who created the harvest record
        created_at (datetime): Timestamp of creation
        updated_at (datetime): Timestamp of last update
    """

    # Basic harvest information
    vineyard = models.ForeignKey(
        Vineyard,
        on_delete=models.CASCADE,
        related_name='harvests',
        help_text="Vineyard where grapes were harvested"
    )
    date = models.DateField(
        help_text="Date of harvest"
    )
    
    # Quantity tracking
    quantity = models.FloatField(
        help_text="Quantity of grapes harvested in kilograms"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the harvest"
    )
    
    # Price fields for supplied grapes
    price_per_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Price per kilogram"
    )
    vat_per_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="VAT percentage (e.g., 25 for 25%)",
        default=0
    )

    # Crushing/Pressing fields
    crushing_date = models.DateField(
        blank=True, 
        null=True, 
        help_text="Date of crushing/pressing"
    )
    juice_yield = models.FloatField(
        blank=True, 
        null=True, 
        help_text="Juice yield in liters"
    )
    pressing_notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Notes about the crushing/pressing process"
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the harvest."""
        return f"Harvest on {self.date} at {self.vineyard.name}"

    @property
    def remaining_juice(self):
        """Calculate the remaining unallocated juice from this harvest."""
        if not self.juice_yield:
            return 0
        allocated = self.harvest_allocations.aggregate(
            total=models.Sum('allocated_volume')
        )['total'] or 0
        return self.juice_yield - allocated

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Harvest'
        verbose_name_plural = 'Harvests'

class HarvestAllocation(models.Model):
    """
    Represents the allocation of juice from a harvest to a specific tank.
    
    This model tracks how juice from harvests is distributed among different tanks,
    enabling tracking of juice movement and tank contents. It ensures proper accounting
    of juice quantities and prevents over-allocation.

    Attributes:
        harvest (Harvest): The harvest from which juice is being allocated
        tank (Tank): The tank receiving the juice allocation
        allocated_volume (float): Volume of juice allocated in liters
        allocation_date (date): Date when the allocation was made
        notes (str, optional): Additional notes about the allocation
        created_by (User): User who created the allocation record
        created_at (datetime): Timestamp of creation
    """

    # Allocation details
    harvest = models.ForeignKey(
        Harvest, 
        on_delete=models.CASCADE, 
        related_name='harvest_allocations',
        help_text="Harvest being allocated"
    )
    tank = models.ForeignKey(
        'cellars.Tank', 
        on_delete=models.CASCADE, 
        related_name='harvest_allocations',
        help_text="Tank receiving the juice"
    )
    allocated_volume = models.FloatField(
        help_text="Volume of juice allocated in liters"
    )
    
    # Allocation timing
    allocation_date = models.DateField(
        help_text="When the allocation was made"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the allocation"
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Validate the allocation to ensure it doesn't exceed available juice.
        
        Raises:
            ValidationError: If allocation would exceed available juice
        """
        if not self.pk:  # Only check on creation
            current_remaining = self.harvest.remaining_juice
            if self.allocated_volume > current_remaining:
                raise ValidationError({
                    'allocated_volume': f'Cannot allocate more than available juice. '
                                      f'Available: {current_remaining}L'
                })

    def save(self, *args, **kwargs):
        """Save the allocation after running validations."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the allocation."""
        return f"{self.allocated_volume}L from {self.harvest} to {self.tank}"

    class Meta:
        ordering = ['-allocation_date', '-created_at']
        verbose_name = 'Harvest Allocation'
        verbose_name_plural = 'Harvest Allocations'
