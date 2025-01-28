from django.db import models
from django.conf import settings

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    oib = models.CharField(max_length=11, unique=True, verbose_name="OIB")  # Croatian tax number
    ibk = models.CharField(max_length=20, blank=True, null=True, verbose_name="IBK")  # Croatian wine producer number
    mibpg = models.CharField(max_length=20, blank=True, null=True, verbose_name="MIBPG")  # Croatian farm number
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Vineyard(models.Model):
    OWNERSHIP_CHOICES = [
        ('owned', 'Owned'),
        ('supplied', 'Supplied'),
    ]

    GRAPE_VARIETY_CHOICES = [
        # Red varieties
        ('plavac_mali', 'Plavac Mali'),
        ('teran', 'Teran'),
        ('babic', 'Babić'),
        ('crljenak', 'Crljenak Kaštelanski (Zinfandel)'),
        ('merlot', 'Merlot'),
        ('cabernet_sauvignon', 'Cabernet Sauvignon'),
        ('syrah', 'Syrah'),
        ('plavina', 'Plavina'),
        ('lasina', 'Lasina'),
        ('marsellan', 'Marsellan'),
        
        # White varieties
        ('malvazija', 'Malvazija Istarska'),
        ('grasevina', 'Graševina'),
        ('posip', 'Pošip'),
        ('debit', 'Debit'),
        ('marastina', 'Maraština'),
        ('kraljevina', 'Kraljevina'),
        ('skrlet', 'Škrlet'),
        ('chardonnay', 'Chardonnay'),
        ('sauvignon_blanc', 'Sauvignon Blanc'),
        ('muskat', 'Muškat'),
        ('vugava', 'Vugava'),
        ('zlahtina', 'Žlahtina'),
        ('malvasia_dubrovacka', 'Malvasija Dubrovačka'),
        
        # Other
        ('other', 'Other (specify in notes)'),
    ]

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in hectares")
    grape_variety = models.CharField(max_length=50, choices=GRAPE_VARIETY_CHOICES)
    ownership_type = models.CharField(max_length=10, choices=OWNERSHIP_CHOICES, default='owned')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='vineyards')
    notes = models.TextField(blank=True)
    arkod_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="ARKOD ID")
    planting_year = models.IntegerField(blank=True, null=True)
    cadastral_parcel = models.CharField(max_length=20, blank=True, null=True)
    cadastral_county = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        variety_display = dict(self.GRAPE_VARIETY_CHOICES).get(self.grape_variety, self.grape_variety)
        return f"{self.name} - {variety_display}"

    class Meta:
        ordering = ['name']
        verbose_name = 'Vineyard'
        verbose_name_plural = 'Vineyards'
