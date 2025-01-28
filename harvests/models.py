from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from vineyards.models import Vineyard

User = get_user_model()

class Harvest(models.Model):
    vineyard = models.ForeignKey(Vineyard, on_delete=models.CASCADE, related_name='harvests')
    date = models.DateField()
    quantity = models.FloatField(help_text="Quantity in kilograms")
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Crushing/Pressing fields
    crushing_date = models.DateField(blank=True, null=True, help_text="Date of crushing/pressing")
    juice_yield = models.FloatField(blank=True, null=True, help_text="Juice yield in liters")
    pressing_notes = models.TextField(blank=True, null=True, help_text="Notes about the crushing/pressing process")

    def __str__(self):
        return f"Harvest on {self.date} at {self.vineyard.name}"

    @property
    def total_allocated_volume(self):
        """Calculate the total volume of juice allocated to tanks."""
        return sum(allocation.allocated_volume for allocation in self.harvest_allocations.all())

    @property
    def remaining_juice(self):
        """Calculate the remaining unallocated juice volume."""
        if not self.juice_yield:
            return 0
        return self.juice_yield - self.total_allocated_volume

    class Meta:
        ordering = ['-date']
        verbose_name = 'Harvest'
        verbose_name_plural = 'Harvests'


class HarvestAllocation(models.Model):
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, related_name='harvest_allocations')
    tank = models.ForeignKey('cellars.Tank', on_delete=models.CASCADE, related_name='harvest_allocations')
    allocated_volume = models.FloatField(help_text="Volume in liters")
    allocation_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.allocated_volume}L from {self.harvest} to {self.tank}"

    def clean(self):
        if not hasattr(self, 'harvest'):
            raise ValidationError("Harvest must be specified")
            
        if not self.harvest.juice_yield:
            raise ValidationError("Cannot allocate juice from a harvest without juice yield")
        
        if not hasattr(self, 'allocated_volume'):
            return
            
        if self.allocated_volume > self.harvest.remaining_juice:
            raise ValidationError(f"Cannot allocate more than the remaining juice volume ({self.harvest.remaining_juice}L)")
        
        if not hasattr(self, 'tank'):
            return
            
        if self.allocated_volume > self.tank.available_space:
            raise ValidationError(f"Cannot allocate more than the available tank space ({self.tank.available_space}L)")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Update tank volume after saving
        self.tank.update_volume(self.allocated_volume)

    class Meta:
        verbose_name = 'Harvest Allocation'
        verbose_name_plural = 'Harvest Allocations'
        ordering = ['-allocation_date', '-created_at']
