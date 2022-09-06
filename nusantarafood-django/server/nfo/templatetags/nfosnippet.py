import re
from django import template

register = template.Library()


@register.inclusion_tag('nfo/templatetags/nfosnippet/small_heading.html')
def small_heading(title, monospace=False):
    return {'title': title, 'monospace': monospace}


@register.simple_tag
def calculate_percentage(count, total):
    return '{:.2f}'.format(100 * count / total)


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v

    return query.urlencode()
