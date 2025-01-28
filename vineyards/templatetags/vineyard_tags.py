from django import template
from vineyards.models import Vineyard

register = template.Library()

@register.simple_tag
def get_vineyard_count():
    """Return the total number of vineyards"""
    return Vineyard.objects.count()

@register.simple_tag
def get_total_vineyard_area():
    """Return the total area of all vineyards"""
    return Vineyard.objects.aggregate(total_area=models.Sum('size'))['total_area'] or 0
