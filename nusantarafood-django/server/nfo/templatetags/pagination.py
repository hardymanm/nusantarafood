import re
from django import template

register = template.Library()


@register.inclusion_tag('nfo/templatetags/pagination.html')
def pagination(page_obj):
    current = page_obj.number
    max = page_obj.paginator.num_pages

    # @TODO: eliminate this magic numbers
    if current - 7 < 0:
        start = 0
    elif current + 8 > max:
        start = max - 15
    else:
        start = current - 7

    page_range = page_obj.paginator.page_range[start: start+15]
    return {'page_range': page_range, 'page_obj': page_obj}


@register.inclusion_tag('nfo/templatetags/pagination_small.html')
def pagination_small(page_obj):
    page_range = page_obj.paginator.page_range
    return {'page_obj': page_obj, 'page_range': page_range}
