import re
from django import template

register = template.Library()

@register.inclusion_tag('nfo/templatetags/pagination.html')
def pagination(paginator, page_obj):
    return {'paginator': paginator, 'page_obj':page_obj }