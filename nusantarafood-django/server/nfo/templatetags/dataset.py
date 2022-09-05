from django import template

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


@register.simple_tag
def task_duration(task):
    try:
        delta = task.date_done - task.date_created
        return f'{delta.seconds:,} sec'
    except AttributeError:
        return ''


@register.simple_tag
def dataset_wordnet_judge_progress(dataset, judge):
    return dataset.wordnetsession_set.filter(judge=judge).first()


@register.simple_tag
def dataset_wiki_judge_progress(dataset, judge):
    return dataset.wikisession_set.filter(judge=judge).first()


@register.simple_tag
def dataset_tabel_judge_progress(dataset, judge):
    return dataset.tabelsession_set.filter(judge=judge).first()


@register.inclusion_tag('nfo/templatetags/dataset/task_status.html')
def task_status(status):
    return {'status': status}


@register.inclusion_tag('nfo/templatetags/dataset/task_row.html')
def dataset_task_row(task_label, task, task_url, pk):
    return {'task_label': task_label, 'task': task, 'task_url': task_url, 'dataset_pk': pk}


@register.inclusion_tag('nfo/templatetags/dataset/judge_session_row.html')
def dataset_judge_session_row(label, dataset, first=False):
    return {'session_label': label, 'dataset': dataset, 'first_row': first}
