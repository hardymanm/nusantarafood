import re
from django import template

register = template.Library()


@register.inclusion_tag('templatetags/navbar/nav_item.html')
def nav_item(request, label, to, pattern=False):
    if pattern:
        active = re.search(pattern, request.path) != None
    else:
        active = request.path == to

    return {'to': to, 'label': label, 'active': active}
