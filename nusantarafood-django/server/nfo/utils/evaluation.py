from nfo import models


def update_wordnet_evaluation(user, form):
    evaluation, _ = models.WordnetEvaluation.objects.get_or_create(judge=user, word=form.cleaned_data['word'])
    evaluation.correct_hypernym = form.cleaned_data['correct_hypernym']
    return evaluation.save()


def update_wiki_evaluation(user, form):
    evaluation, _ = models.WikiEvaluation.objects.get_or_create(judge=user, recipe=form.cleaned_data['recipe'])
    evaluation.suggested_categories = form.cleaned_data['suggested_categories']
    return evaluation.save()


def update_tabel_evaluation(user, form):
    evaluation, _ = models.TabelEvaluation.objects.get_or_create(judge=user, recipe=form.cleaned_data['recipe'])
    evaluation.suggested_categories = form.cleaned_data['suggested_categories']
    evaluation.correct_categories.set(form.cleaned_data['correct_categories'])
    return evaluation.save()