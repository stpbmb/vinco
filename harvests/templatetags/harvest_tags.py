from django import template
from django.db.models import Sum
from harvests.models import Harvest

register = template.Library()

@register.simple_tag
def get_total_harvest_quantity():
    """Return the total quantity of all harvests"""
    return Harvest.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

@register.simple_tag
def get_total_juice_yield():
    """Return the total juice yield from all harvests"""
    return Harvest.objects.aggregate(total_yield=Sum('juice_yield'))['total_yield'] or 0
