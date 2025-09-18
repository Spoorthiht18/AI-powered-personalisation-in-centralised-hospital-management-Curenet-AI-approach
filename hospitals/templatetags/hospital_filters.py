from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    return dictionary.get(key)

@register.filter
def format_distance(distance):
    """Format distance for display."""
    if distance < 1:
        return f"{int(distance * 1000)}m"
    else:
        return f"{distance:.1f}km"
