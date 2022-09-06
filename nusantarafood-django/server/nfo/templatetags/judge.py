from django import template

from nfo.models import Dataset, WordnetSession, WikiSession, TabelSession

register = template.Library()


@register.simple_tag
def pending_session(user):
    total = Dataset.objects.count() * 3
    wordnet = Dataset.objects.filter(wordnetsession__judge=user).count()
    wiki = Dataset.objects.filter(wikisession__judge=user).count()
    tabel = Dataset.objects.filter(tabelsession__judge=user).count()
    return total - wordnet - wiki - tabel


@register.simple_tag
def in_progress_session(user):
    wordnet = WordnetSession.objects.filter(judge=user, is_finished=False).count()
    wiki = WikiSession.objects.filter(judge=user, is_finished=False).count()
    tabel = TabelSession.objects.filter(judge=user, is_finished=False).count()
    return wordnet + wiki + tabel


@register.simple_tag
def completed_session(user):
    wordnet = WordnetSession.objects.filter(judge=user, is_finished=True).count()
    wiki = WikiSession.objects.filter(judge=user, is_finished=True).count()
    tabel = TabelSession.objects.filter(judge=user, is_finished=True).count()
    return wordnet + wiki + tabel
