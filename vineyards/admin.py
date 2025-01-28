from django.contrib import admin
from .models import (
    Vineyard,
    Supplier,
)

# Register all models in one place

@admin.register(Vineyard)
class VineyardAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'size', 'grape_variety', 'ownership_type', 'supplier')
    list_filter = ('ownership_type', 'grape_variety')
    search_fields = ('name', 'location', 'grape_variety')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'oib', 'ibk', 'mibpg')
    search_fields = ('name', 'oib', 'ibk', 'mibpg')
