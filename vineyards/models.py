from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    oib = models.CharField(max_length=11, unique=True, help_text="OIB (11-digit number)")
    ibk = models.CharField(max_length=50, unique=True, help_text="IBK number")
    mibpg = models.CharField(max_length=50, unique=True, help_text="MIBPG number")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Vineyard(models.Model):
    OWNERSHIP_CHOICES = [
        ('owned', 'Owned'),
        ('supplied', 'Supplied'),
    ]

    # Predefined grape varieties
    GRAPE_VARIETY_CHOICES = [
        ('cabernet_sauvignon', 'Cabernet Sauvignon'),
        ('merlot', 'Merlot'),
        ('pinot_noir', 'Pinot Noir'),
        ('chardonnay', 'Chardonnay'),
        ('sauvignon_blanc', 'Sauvignon Blanc'),
        ('syrah', 'Syrah'),
        ('zinfandel', 'Zinfandel'),
        ('riesling', 'Riesling'),
        ('tempranillo', 'Tempranillo'),
        ('sangiovese', 'Sangiovese'),
        ('malbec', 'Malbec'),
        ('grenache', 'Grenache'),
        ('nebbiolo', 'Nebbiolo'),
        ('pinot_grigio', 'Pinot Grigio'),
        ('viognier', 'Viognier'),
        ('cabernet_franc', 'Cabernet Franc'),
        ('barbera', 'Barbera'),
        ('moscato', 'Moscato'),
        ('shiraz', 'Shiraz'),
        ('carmenere', 'Carmenere'),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    size = models.FloatField(help_text="Size in hectares")
    grape_variety = models.CharField(max_length=255, choices=GRAPE_VARIETY_CHOICES)  # Updated field
    ownership_type = models.CharField(max_length=50, choices=OWNERSHIP_CHOICES)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='vineyards')
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vineyards')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields
    arkod_id = models.IntegerField(blank=True, null=True, help_text="ARKOD ID number")
    planting_year = models.IntegerField(blank=True, null=True, help_text="Year the vineyard was planted")
    cadastral_parcel = models.CharField(max_length=255, blank=True, null=True, help_text="Cadastral parcel information")
    cadastral_county = models.CharField(max_length=255, blank=True, null=True, help_text="Cadastral county information")

    def __str__(self):
        return self.name


from django.core.exceptions import ValidationError

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

    def total_allocated_volume(self):
        """Calculate the total volume of juice allocated to tanks."""
        return sum(allocation.allocated_volume for allocation in self.allocations.all())

    def remaining_juice(self):
        """Calculate the remaining juice volume to be allocated."""
        if self.juice_yield is not None:
            return self.juice_yield - self.total_allocated_volume()
        return 0



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
        return f"{self.name} ({self.tank_type}) in {self.cellar.name}"

    def update_volume(self, volume):
        """Update the current volume of the tank."""
        self.current_volume += volume
        if self.current_volume < 0:
            self.current_volume = 0
        self.save()


class CrushedJuiceAllocation(models.Model):
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, related_name='allocations')
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='allocations')
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
        # Ensure allocated_volume is a positive number
        if self.allocated_volume < 0:
            raise ValidationError({
                'allocated_volume': 'Allocated volume must be a positive number.'
            })
        # Ensure the allocated volume does not exceed the tank's available capacity
        if self.allocated_volume > (self.tank.capacity - self.tank.current_volume):
            raise ValidationError({
                'allocated_volume': f'Allocated volume exceeds available capacity in {self.tank.name}.'
            })
        # Ensure the allocated volume does not exceed the remaining juice from the harvest
        if self.allocated_volume > self.harvest.remaining_juice():
            raise ValidationError({
                'allocated_volume': f'Allocated volume exceeds remaining juice from {self.harvest}.'
            })
