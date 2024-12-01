from django import template
from operator import attrgetter

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def dictsortby(value, arg):
    """Sort a list of dictionaries/objects by a common attribute."""
    return sorted(value, key=attrgetter(arg))

@register.filter
def selectattr(value, args):
    """Filter a list of objects by attribute value.
    Usage: value|selectattr:"attribute,value"
    """
    if not args or ',' not in args:
        return []
    
    attr, val = args.split(',', 1)
    return [item for item in value if str(getattr(item, attr.strip(), None)) == val.strip()]

@register.filter
def list(value):
    """Convert an iterable to a list."""
    return list(value) 