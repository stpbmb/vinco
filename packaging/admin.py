from django.contrib import admin
from .models import Bottle, Label, Closure, Box

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('name', 'bottle_type', 'volume', 'glass_color', 'stock', 'supplier', 'price')
    list_filter = ('bottle_type', 'glass_color', 'supplier')
    search_fields = ('name', 'supplier', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by during the first save
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'label_type', 'material', 'stock', 'supplier', 'price')
    list_filter = ('label_type', 'material', 'supplier')
    search_fields = ('name', 'supplier', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = ('name', 'closure_type', 'material', 'color', 'stock', 'supplier', 'price')
    list_filter = ('closure_type', 'material', 'supplier')
    search_fields = ('name', 'supplier', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'box_type', 'material', 'bottle_capacity', 'stock', 'supplier', 'price')
    list_filter = ('box_type', 'material', 'supplier')
    search_fields = ('name', 'supplier', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
