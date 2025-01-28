from django.contrib import admin
from .models import Cellar, Tank, CrushedJuiceAllocation, TankHistory

@admin.register(Cellar)
class CellarAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')
    search_fields = ('name', 'location', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('name', 'cellar', 'tank_type', 'capacity', 'current_volume')
    list_filter = ('cellar', 'tank_type')
    search_fields = ('name', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(CrushedJuiceAllocation)
class CrushedJuiceAllocationAdmin(admin.ModelAdmin):
    list_display = ('harvest', 'tank', 'allocated_volume', 'allocation_date')
    list_filter = ('allocation_date', 'tank__cellar')
    search_fields = ('notes', 'harvest__vineyard__name', 'tank__name')
    date_hierarchy = 'allocation_date'
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TankHistory)
class TankHistoryAdmin(admin.ModelAdmin):
    list_display = ('tank', 'operation_type', 'date', 'volume')
    list_filter = ('operation_type', 'date', 'tank__cellar')
    search_fields = ('notes', 'tank__name')
    date_hierarchy = 'date'
    readonly_fields = ('created_by', 'created_at')
