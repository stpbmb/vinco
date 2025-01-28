from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from harvests.models import Harvest

User = get_user_model()

class Cellar(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the cellar")
    location = models.CharField(max_length=200, help_text="Location of the cellar")
    capacity = models.FloatField(help_text="Total capacity in liters")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the cellar")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Cellar'
        verbose_name_plural = 'Cellars'

class Tank(models.Model):
    TANK_TYPES = [
        ('stainless_steel', 'Stainless Steel'),
        ('oak_barrel', 'Oak Barrel'),
        ('concrete', 'Concrete'),
        ('fiberglass', 'Fiberglass'),
    ]

    cellar = models.ForeignKey(Cellar, on_delete=models.CASCADE, related_name='tanks')
    name = models.CharField(max_length=100, help_text="Name or identifier of the tank")
    tank_type = models.CharField(max_length=50, choices=TANK_TYPES, help_text="Type of tank")
    capacity = models.FloatField(help_text="Capacity in liters")
    current_volume = models.FloatField(default=0, help_text="Current volume in liters")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the tank")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_tank_type_display()}) in {self.cellar.name}"

    @property
    def available_space(self):
        """Calculate available space in the tank"""
        return self.capacity - self.current_volume

    def update_volume(self, volume_change):
        """Update the current volume of the tank."""
        new_volume = self.current_volume + volume_change
        if new_volume < 0:
            raise ValidationError("Tank volume cannot be negative")
        if new_volume > self.capacity:
            raise ValidationError(f"Volume exceeds tank capacity of {self.capacity} liters")
        self.current_volume = new_volume
        self.save()

    class Meta:
        ordering = ['cellar', 'name']
        verbose_name = 'Tank'
        verbose_name_plural = 'Tanks'
        unique_together = ['cellar', 'name']

class CrushedJuiceAllocation(models.Model):
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, related_name='crushed_juice_allocations')
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='crushed_juice_allocations')
    allocated_volume = models.FloatField(help_text="Volume allocated to this tank in liters")
    allocation_date = models.DateField(help_text="Date of allocation")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the allocation")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.allocated_volume} liters from {self.harvest} to {self.tank}"

    def clean(self):
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
        ordering = ['-allocation_date']
        verbose_name = 'Crushed Juice Allocation'
        verbose_name_plural = 'Crushed Juice Allocations'

class TankHistory(models.Model):
    OPERATION_TYPES = [
        ('allocation', 'Allocation from Harvest'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('bottling', 'Bottling'),
    ]

    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='history')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    date = models.DateField()
    volume = models.FloatField(help_text="Volume change in liters (positive for in, negative for out)")
    source = models.ForeignKey('Tank', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_out')
    destination = models.ForeignKey('Tank', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_in')
    harvest = models.ForeignKey('harvests.Harvest', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

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
        ordering = ['-date', '-created_at']
        verbose_name = 'Tank History'
        verbose_name_plural = 'Tank Histories'
