from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Bottle(models.Model):
    """Model for wine bottles."""
    BOTTLE_TYPES = [
        ('bordeaux', 'Bordeaux'),
        ('burgundy', 'Burgundy'),
        ('champagne', 'Champagne'),
        ('rhine', 'Rhine'),
        ('other', 'Other'),
    ]

    GLASS_COLORS = [
        ('clear', 'Clear'),
        ('green', 'Green'),
        ('dark_green', 'Dark Green'),
        ('amber', 'Amber'),
        ('blue', 'Blue'),
    ]

    name = models.CharField(max_length=255, help_text="Name or identifier of the bottle")
    bottle_type = models.CharField(max_length=50, choices=BOTTLE_TYPES, help_text="Type/style of the bottle")
    volume = models.FloatField(help_text="Volume in milliliters")
    glass_color = models.CharField(max_length=50, choices=GLASS_COLORS, help_text="Color of the glass")
    height = models.FloatField(help_text="Height in millimeters")
    diameter = models.FloatField(help_text="Diameter in millimeters")
    weight = models.FloatField(help_text="Weight in grams")
    supplier = models.CharField(max_length=255, help_text="Supplier of the bottles")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    stock = models.IntegerField(default=0, help_text="Current stock quantity")
    minimum_stock = models.IntegerField(default=0, help_text="Minimum stock level for reordering")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the bottle")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.volume}ml {self.get_bottle_type_display()})"

    class Meta:
        ordering = ['name']

class Label(models.Model):
    """Model for wine labels."""
    LABEL_TYPES = [
        ('front', 'Front Label'),
        ('back', 'Back Label'),
        ('neck', 'Neck Label'),
    ]

    MATERIAL_TYPES = [
        ('paper', 'Paper'),
        ('synthetic', 'Synthetic'),
        ('metallic', 'Metallic'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, help_text="Name or identifier of the label")
    label_type = models.CharField(max_length=50, choices=LABEL_TYPES, help_text="Type of label")
    material = models.CharField(max_length=50, choices=MATERIAL_TYPES, help_text="Material of the label")
    width = models.FloatField(help_text="Width in millimeters")
    height = models.FloatField(help_text="Height in millimeters")
    supplier = models.CharField(max_length=255, help_text="Supplier of the labels")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    stock = models.IntegerField(default=0, help_text="Current stock quantity")
    minimum_stock = models.IntegerField(default=0, help_text="Minimum stock level for reordering")
    design_file = models.FileField(upload_to='label_designs/', blank=True, null=True, help_text="Design file for the label")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the label")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_label_type_display()})"

    class Meta:
        ordering = ['name']

class Closure(models.Model):
    """Model for bottle closures (caps, corks, etc.)."""
    CLOSURE_TYPES = [
        ('cork_natural', 'Natural Cork'),
        ('cork_synthetic', 'Synthetic Cork'),
        ('screw_cap', 'Screw Cap'),
        ('crown_cap', 'Crown Cap'),
        ('glass_stopper', 'Glass Stopper'),
        ('other', 'Other'),
    ]

    MATERIAL_TYPES = [
        ('cork', 'Cork'),
        ('synthetic', 'Synthetic'),
        ('aluminum', 'Aluminum'),
        ('steel', 'Steel'),
        ('glass', 'Glass'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, help_text="Name or identifier of the closure")
    closure_type = models.CharField(max_length=50, choices=CLOSURE_TYPES, help_text="Type of closure")
    material = models.CharField(max_length=50, choices=MATERIAL_TYPES, help_text="Material of the closure")
    color = models.CharField(max_length=50, help_text="Color of the closure")
    diameter = models.FloatField(help_text="Diameter in millimeters")
    height = models.FloatField(help_text="Height in millimeters")
    supplier = models.CharField(max_length=255, help_text="Supplier of the closures")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    stock = models.IntegerField(default=0, help_text="Current stock quantity")
    minimum_stock = models.IntegerField(default=0, help_text="Minimum stock level for reordering")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the closure")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_closure_type_display()})"

    class Meta:
        ordering = ['name']

class Box(models.Model):
    """Model for packaging boxes."""
    BOX_TYPES = [
        ('single', 'Single Bottle'),
        ('double', 'Double Bottle'),
        ('triple', 'Triple Bottle'),
        ('six_pack', 'Six Pack'),
        ('twelve_pack', 'Twelve Pack'),
        ('shipping', 'Shipping Box'),
        ('gift', 'Gift Box'),
        ('other', 'Other'),
    ]

    MATERIAL_TYPES = [
        ('cardboard', 'Cardboard'),
        ('wood', 'Wood'),
        ('plastic', 'Plastic'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, help_text="Name or identifier of the box")
    box_type = models.CharField(max_length=50, choices=BOX_TYPES, help_text="Type of box")
    material = models.CharField(max_length=50, choices=MATERIAL_TYPES, help_text="Material of the box")
    bottle_capacity = models.IntegerField(help_text="Number of bottles the box can hold")
    length = models.FloatField(help_text="Length in millimeters")
    width = models.FloatField(help_text="Width in millimeters")
    height = models.FloatField(help_text="Height in millimeters")
    weight = models.FloatField(help_text="Weight in grams")
    supplier = models.CharField(max_length=255, help_text="Supplier of the boxes")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    stock = models.IntegerField(default=0, help_text="Current stock quantity")
    minimum_stock = models.IntegerField(default=0, help_text="Minimum stock level for reordering")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the box")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_box_type_display()} - {self.bottle_capacity} bottles)"

    class Meta:
        ordering = ['name']
        verbose_name_plural = "boxes"
