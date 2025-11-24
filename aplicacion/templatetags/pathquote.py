from urllib.parse import quote
from django import template

register = template.Library()

@register.filter
def pathquote(value):
    """Quote a filesystem path for safe use in URLs while preserving slashes."""
    if not value:
        return ''
    # On Windows paths might contain backslashes; normalize to forward slashes
    v = value.replace('\\', '/')
    # If path contains a leading 'data/', remove it (templates already did this in places)
    # We'll not remove it here; caller should cut if needed. But supporting both:
    if v.startswith('data/'):
        v = v[len('data/'):]
    return quote(v, safe='/' )
