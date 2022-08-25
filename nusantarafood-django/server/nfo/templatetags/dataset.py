import re
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def wordnet_session(context):
    dataset = context['object']
    request = context['request']
    return dataset.wordnetsession_set.filter(judge=request.user).first()


@register.simple_tag(takes_context=True)
def wiki_session(context):
    dataset = context['object']
    request = context['request']
    return dataset.wikisession_set.filter(judge=request.user).first()


@register.simple_tag(takes_context=True)
def tabel_session(context):
    dataset = context['object']
    request = context['request']
    return dataset.tabelsession_set.filter(judge=request.user).first()
