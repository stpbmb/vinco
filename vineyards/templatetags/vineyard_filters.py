from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter(name='default_if_none_or_empty')
def default_if_none_or_empty(value, default="-"):
    """Return default value if value is None or empty string."""
    if value is None or value == '':
        return default
    return value

@register.simple_tag
def url_replace(request, field, value):
    """
    Template tag to replace a GET parameter while keeping the others.
    
    Usage:
    <a href="?{% url_replace request 'page' 3 %}">Page 3</a>
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return urlencode(dict_)
