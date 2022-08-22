from nfo import models


def update_wordnet_evaluation(user, form):
    evaluation, _ = models.WordnetEvaluation.objects.get_or_create(judge=user, word=form.cleaned_data['word'])
    evaluation.correct_hypernym = form.cleaned_data['correct_hypernym']
    return evaluation.save()
