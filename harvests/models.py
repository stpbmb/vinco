"""
Models for managing grape harvests and juice allocations in the wine production process.

This module contains models for tracking grape harvests from vineyards and managing the allocation
of juice to different tanks. It handles harvest details, pressing information, and juice distribution
throughout the production process.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from core.models import TenantModel
from vineyards.models import Vineyard
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Harvest(TenantModel):
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
        juice_yield (float, optional): Volume of juice obtained in liters
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
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
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
    juice_yield = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Volume of juice obtained in liters",
        default=0
    )
    pressing_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about the crushing/pressing process"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='harvest_created',
        null=True,
        blank=True,
        default=None
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='harvest_updated',
        null=True,
        blank=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the harvest."""
        return f"{self.vineyard.name} - {self.date}"

    @property
    def available_juice(self):
        """Calculate available juice volume that can still be allocated."""
        if not self.juice_yield:
            return 0
            
        allocated = self.allocations.aggregate(
            total=Sum('allocated_volume')
        )['total'] or 0
        
        return float(self.juice_yield) - float(allocated)

    def clean(self):
        """
        Validate harvest constraints.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()

        if self.quantity is not None and self.juice_yield is not None:
            if self.quantity <= 0:
                raise ValidationError("Harvest quantity must be greater than 0")
            if self.juice_yield < 0:
                raise ValidationError("Juice yield must be greater than or equal to 0")

            # For existing harvests, check if reducing quantity would go below allocated volume
            if self.pk:
                allocated_volume = self.allocations.aggregate(
                    total=Sum('allocated_volume')
                )['total'] or 0

                if self.juice_yield < allocated_volume:
                    raise ValidationError(
                        f"Cannot reduce juice volume below allocated amount ({allocated_volume}L)"
                    )

        if self.vineyard.organization != self.organization:
            raise ValidationError('Vineyard must belong to the same organization')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Harvest'
        verbose_name_plural = 'Harvests'

class HarvestAllocation(TenantModel):
    """
    Represents an allocation of juice from a harvest to a tank.
    
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
        on_delete=models.CASCADE,  # Delete allocations when harvest is deleted
        related_name='allocations'
    )
    tank = models.ForeignKey(
        'cellars.Tank',  # Use string reference to avoid circular import
        on_delete=models.CASCADE,  # Delete allocations when tank is deleted
        related_name='harvest_allocations'
    )
    allocated_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    allocation_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_allocations'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='updated_allocations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validate allocation constraints.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()

        if not self.allocated_volume:
            raise ValidationError("Allocated volume is required")

        if self.allocated_volume <= 0:
            raise ValidationError("Allocated volume must be greater than 0")

        # Check if allocation exceeds available juice
        if self.harvest:
            available = self.harvest.available_juice
            if self.pk:  # For updates, add back this allocation's current volume
                current = HarvestAllocation.objects.get(pk=self.pk)
                available += current.allocated_volume

            if self.allocated_volume > available:
                raise ValidationError(
                    f"Cannot allocate more than available juice ({available:.2f}L)"
                )

        # Check if allocation would exceed tank capacity
        from cellars.models import Tank
        if self.tank:
            current_volume = self.tank.current_volume
            if self.pk:  # For updates, subtract this allocation's current volume
                current = HarvestAllocation.objects.get(pk=self.pk)
                current_volume -= current.allocated_volume

            if current_volume + self.allocated_volume > self.tank.capacity:
                raise ValidationError(
                    "Allocation would exceed tank capacity"
                )

        if self.harvest.organization != self.organization:
            raise ValidationError('Harvest must belong to the same organization')
        if self.tank.organization != self.organization:
            raise ValidationError('Tank must belong to the same organization')

    def save(self, *args, **kwargs):
        """Save the allocation and update the tank's volume."""
        from cellars.models import Tank, TankHistory
        
        is_new = self.pk is None
        
        if not is_new:
            # Get the old allocation volume for updates
            old_allocation = HarvestAllocation.objects.get(pk=self.pk)
            # Only update tank volumes if the volume or tank has changed
            if (old_allocation.allocated_volume != self.allocated_volume or 
                old_allocation.tank != self.tank):
                # Remove volume from old tank
                old_allocation.tank.update_volume(-float(old_allocation.allocated_volume))
                # Create history record for volume removal
                TankHistory.objects.create(
                    tank=old_allocation.tank,
                    operation_type='allocation',
                    date=self.allocation_date,
                    volume=-float(old_allocation.allocated_volume),
                    harvest=self.harvest,
                    created_by=self.updated_by or self.created_by,
                    notes=f"Removed allocation of {old_allocation.allocated_volume}L"
                )
                
                if old_allocation.tank != self.tank:
                    # Add volume to new tank if tank changed
                    self.tank.update_volume(float(self.allocated_volume))
                    # Create history record for new tank
                    TankHistory.objects.create(
                        tank=self.tank,
                        operation_type='allocation',
                        date=self.allocation_date,
                        volume=float(self.allocated_volume),
                        harvest=self.harvest,
                        created_by=self.updated_by or self.created_by,
                        notes=f"Added allocation of {self.allocated_volume}L"
                    )
        
        # Save the allocation
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Add volume to tank for new allocations or when only volume changed
        if is_new or (not is_new and old_allocation.tank == self.tank):
            self.tank.update_volume(float(self.allocated_volume))
            # Create history record for volume addition
            TankHistory.objects.create(
                tank=self.tank,
                operation_type='allocation',
                date=self.allocation_date,
                volume=float(self.allocated_volume),
                harvest=self.harvest,
                created_by=self.updated_by or self.created_by,
                notes=f"{'Added' if is_new else 'Updated'} allocation of {self.allocated_volume}L"
            )

    def __str__(self):
        return f"{self.allocated_volume}L from {self.harvest} to {self.tank}"

    class Meta:
        ordering = ['-allocation_date', '-created_at']
        verbose_name = 'Harvest Allocation'
        verbose_name_plural = 'Harvest Allocations'

@receiver(pre_delete, sender=HarvestAllocation)
def remove_allocation_from_tank(sender, instance, **kwargs):
    """Remove the allocated volume from the tank when an allocation is deleted."""
    from cellars.models import Tank, TankHistory
    
    # Remove volume from tank
    instance.tank.update_volume(-float(instance.allocated_volume))
    
    # Create history record
    TankHistory.objects.create(
        tank=instance.tank,
        operation_type='allocation',
        date=instance.allocation_date,
        volume=-float(instance.allocated_volume),
        harvest=instance.harvest,
        created_by=instance.updated_by or instance.created_by,
        notes=f"Removed allocation of {instance.allocated_volume}L (allocation deleted)"
    )
