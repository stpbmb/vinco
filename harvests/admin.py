from django.contrib import admin
from .models import Harvest

@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('vineyard', 'date', 'quantity', 'juice_yield', 'crushing_date')
    list_filter = ('date', 'crushing_date', 'vineyard__grape_variety')
    search_fields = ('vineyard__name', 'notes', 'pressing_notes')
    date_hierarchy = 'date'
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by during the first save
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
