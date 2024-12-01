from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

# Add a simple test filter to verify registration
@register.filter
def add_one(value):
    """Adds one to the given value"""
    try:
        return float(value) + 1
    except (ValueError, TypeError):
        return 0 