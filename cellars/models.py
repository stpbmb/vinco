from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.core.validators import MinValueValidator
from harvests.models import Harvest
from decimal import Decimal

User = get_user_model()

class Cellar(models.Model):
    """
    Model for managing wine cellars.

    This model tracks information about the cellar, including its name, location,
    and notes. The capacity is automatically computed as the sum of all tank capacities.
    """

    # Basic cellar information
    name = models.CharField(
        max_length=100,
        help_text="Name of the cellar"
    )
    location = models.CharField(
        max_length=200,
        help_text="Location of the cellar"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the cellar"
    )

    # Relationship with the user who created the cellar
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created the cellar"
    )

    # Timestamps for creation and update
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the cellar was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the cellar was last updated"
    )

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        """
        Calculate total capacity of the cellar by summing all tank capacities.
        Returns the total capacity in liters.
        """
        return self.tanks.aggregate(total=Sum('capacity'))['total'] or Decimal('0.00')

    @property
    def total_current_volume(self):
        """
        Calculate total current volume in the cellar by summing all tank volumes.
        Returns the total volume in liters.
        """
        return self.tanks.aggregate(total=Sum('current_volume'))['total'] or Decimal('0.00')

    @property
    def available_capacity(self):
        """
        Calculate available capacity in the cellar.
        Returns the available capacity in liters.
        """
        return self.capacity - self.total_current_volume

    class Meta:
        """
        Metadata for the Cellar model.

        This includes the ordering of cellar instances, the verbose name, and the
        plural verbose name.
        """
        ordering = ['name']
        verbose_name = 'Cellar'
        verbose_name_plural = 'Cellars'

class Tank(models.Model):
    """
    Model for managing wine tanks.

    This model tracks information about the tank, including its name, type, capacity,
    current volume, and notes. It also maintains relationships with the cellar it
    belongs to and the user who created it.
    """

    # Tank status choices
    TANK_TYPES = [
        ('stainless_steel', 'Stainless Steel'),
        ('oak_barrel', 'Oak Barrel'),
        ('concrete', 'Concrete'),
        ('fiberglass', 'Fiberglass'),
    ]

    # Basic tank information
    cellar = models.ForeignKey(
        Cellar,
        on_delete=models.CASCADE,
        related_name='tanks',
        help_text="Cellar that the tank belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name or identifier of the tank"
    )
    tank_type = models.CharField(
        max_length=20,
        choices=TANK_TYPES,
        default='stainless_steel',
        help_text="Type of tank"
    )
    capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Capacity in liters"
    )
    current_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current volume in liters"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the tank"
    )

    # Relationship with the user who created the tank
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who created the tank"
    )

    # Timestamps for creation and update
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the tank was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the tank was last updated"
    )

    def __str__(self):
        tank_type_display = dict(self.TANK_TYPES)[self.tank_type]
        return f"{self.name} ({tank_type_display}) in {self.cellar.name}"

    def clean(self):
        """
        Validate tank capacity and volume constraints.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()

        if self.current_volume and self.current_volume > self.capacity:
            raise ValidationError("Current volume cannot exceed tank capacity")

        if self.pk:  # Only check for existing tanks
            old_instance = Tank.objects.get(pk=self.pk)
            if self.capacity < old_instance.current_volume:
                raise ValidationError("Tank capacity cannot be reduced below current volume")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def available_space(self):
        """
        Calculate available space in the tank.

        Returns the difference between the tank's capacity and its current volume.
        """
        return float(self.capacity - self.current_volume)

    def update_volume(self, volume_change):
        """
        Update the current volume of the tank.

        Args:
            volume_change (float): The change in volume to apply to the tank.

        Raises:
            ValidationError: If the new volume would be negative or exceed the tank's capacity.
        """
        volume_change = Decimal(str(volume_change))
        new_volume = self.current_volume + volume_change
        if new_volume < 0:
            raise ValidationError("Tank volume cannot be negative")
        if new_volume > self.capacity:
            raise ValidationError(f"Volume exceeds tank capacity of {self.capacity} liters")
        self.current_volume = new_volume
        self.save()

    class Meta:
        """
        Metadata for the Tank model.

        This includes the ordering of tank instances, the verbose name, the plural
        verbose name, and a unique constraint on the cellar and name fields.
        """
        ordering = ['cellar', 'name']
        verbose_name = 'Tank'
        verbose_name_plural = 'Tanks'
        unique_together = ['cellar', 'name']

class CrushedJuiceAllocation(models.Model):
    """
    Model for managing crushed juice allocations.

    This model tracks information about the allocation of crushed juice to a tank,
    including the harvest it came from, the tank it was allocated to, the volume
    allocated, and the date of allocation.
    """

    # Basic allocation information
    harvest = models.ForeignKey(
        Harvest,
        on_delete=models.CASCADE,
        related_name='crushed_juice_allocations',
        help_text="Harvest that the juice came from"
    )
    tank = models.ForeignKey(
        Tank,
        on_delete=models.CASCADE,
        related_name='crushed_juice_allocations',
        help_text="Tank that the juice was allocated to"
    )
    allocated_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Volume allocated to this tank in liters"
    )
    allocation_date = models.DateField(
        help_text="Date of allocation"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the allocation"
    )

    # Relationship with the user who created the allocation
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created the allocation"
    )

    # Timestamps for creation and update
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the allocation was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the allocation was last updated"
    )

    def __str__(self):
        return f"{self.allocated_volume} liters from {self.harvest} to {self.tank}"

    def clean(self):
        """
        Validate the allocation.

        Ensures that:
        1. The allocated volume is positive
        2. The allocated volume does not exceed the available capacity in the tank
        3. The allocated volume does not exceed the remaining juice from the harvest
        """
        super().clean()
        if self.allocated_volume < 0:
            raise ValidationError({
                'allocated_volume': 'Allocated volume must be a positive number.'
            })
        if self.allocated_volume > (self.tank.capacity - self.tank.current_volume):
            raise ValidationError({
                'allocated_volume': f'Allocated volume exceeds available capacity in {self.tank.name}.'
            })
        if self.allocated_volume > self.harvest.remaining_juice:
            raise ValidationError({
                'allocated_volume': f'Allocated volume exceeds remaining juice from {self.harvest}.'
            })

    def save(self, *args, **kwargs):
        """
        Save the allocation and update the tank's volume.

        Also creates a history entry for the allocation.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        self.tank.update_volume(self.allocated_volume)
        # Create history entry for the allocation
        TankHistory.objects.create(
            tank=self.tank,
            operation_type='allocation',
            date=self.allocation_date,
            volume=self.allocated_volume,
            harvest=self.harvest,
            notes=self.notes,
            created_by=self.created_by
        )

    class Meta:
        """
        Metadata for the CrushedJuiceAllocation model.

        This includes the ordering of allocation instances and the verbose name.
        """
        ordering = ['-allocation_date']
        verbose_name = 'Crushed Juice Allocation'
        verbose_name_plural = 'Crushed Juice Allocations'

class TankHistory(models.Model):
    """
    Model for managing tank history.

    This model tracks information about the history of a tank, including the type
    of operation, the date, the volume change, and any relevant notes.
    """

    # Operation type choices
    OPERATION_TYPES = [
        ('allocation', 'Allocation from Harvest'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('bottling', 'Bottling'),
    ]

    # Basic history information
    tank = models.ForeignKey(
        Tank,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Tank that the history entry belongs to"
    )
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPES,
        help_text="Type of operation"
    )
    date = models.DateField(
        help_text="Date of the operation"
    )
    volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Volume change in liters (positive for in, negative for out)"
    )
    source = models.ForeignKey(
        'Tank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_out',
        help_text="Source tank for transfer operations"
    )
    destination = models.ForeignKey(
        'Tank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_in',
        help_text="Destination tank for transfer operations"
    )
    harvest = models.ForeignKey(
        'harvests.Harvest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Harvest associated with the operation"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the operation"
    )

    # Relationship with the user who created the history entry
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created the history entry"
    )

    # Timestamp for creation
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the history entry was created"
    )

    def __str__(self):
        if self.operation_type == 'allocation':
            return f"{self.date}: Allocated {self.volume}L from harvest to {self.tank}"
        elif self.operation_type == 'transfer_in':
            return f"{self.date}: Transferred {self.volume}L from {self.source} to {self.tank}"
        elif self.operation_type == 'transfer_out':
            return f"{self.date}: Transferred {self.volume}L from {self.tank} to {self.destination}"
        elif self.operation_type == 'bottling':
            return f"{self.date}: Bottled {abs(self.volume)}L from {self.tank}"
        return f"{self.date}: {self.get_operation_type_display()} {self.volume}L"

    class Meta:
        """
        Metadata for the TankHistory model.

        This includes the ordering of history instances and the verbose name.
        """
        ordering = ['-date', '-created_at']
        verbose_name = 'Tank History'
        verbose_name_plural = 'Tank Histories'
