import re
from django import template

register = template.Library()


@register.inclusion_tag('nfo/templatetags/nfosnippet/small_heading.html')
def small_heading(title, monospace=False):
    return {'title': title, 'monospace': monospace}
