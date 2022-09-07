from django import template

from nfo.models import Dataset, JudgeSession

register = template.Library()


@register.simple_tag
def pending_session(user):
    total = Dataset.objects.count() * 3
    session_count = Dataset.objects.filter(judgesession__judge=user).count()
    return total - session_count


@register.simple_tag
def in_progress_session(user):
    return JudgeSession.objects.filter(judge=user, is_finished=False).count()


@register.simple_tag
def completed_session(user):
    return JudgeSession.objects.filter(judge=user, is_finished=True).count()
