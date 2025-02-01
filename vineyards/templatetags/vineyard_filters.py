from django import template

register = template.Library()

@register.filter(name='default_if_none_or_empty')
def default_if_none_or_empty(value, default="-"):
    """Return default value if value is None or empty string."""
    if value is None or value == '':
        return default
    return value
