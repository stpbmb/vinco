from django import template
from vineyards.models import Vineyard

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def get_grape_variety_display(value):
    """Convert grape variety choice to display name."""
    try:
        choices_dict = dict(Vineyard.GRAPE_VARIETY_CHOICES)
        return choices_dict.get(value, value)
    except (ValueError, TypeError):
        return value
