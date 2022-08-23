from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse
from django.contrib import messages

from nfo import models
from nfo.forms import TabelEvaluationForm, WikiEvaluationForm, WordnetEvaluationForm
from nfo.utils.evaluation import update_tabel_evaluation, update_wiki_evaluation, update_wordnet_evaluation


def index(request):
    return render(request, 'nfo/index.html', {})


class JudgeTabelList(ListView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_list.html'


class JudgeTabelInstruction(DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_instruction.html'


class JudgeTabelDone(DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_done.html'


class JudgeWikiList(ListView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_list.html'


class JudgeWikiInstruction(DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_instruction.html'


class JudgeWikiDone(DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_done.html'


class JudgeWordnetList(ListView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_list.html'


class JudgeWordnetInstruction(DetailView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_instruction.html'


class JudgeWordnetDone(DetailView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_done.html'


def judge_wordnet_item(request, pk, page):
    template_name = 'nfo/judge/wordnet_item.html'
    object = models.LdaModel.objects.get(pk=pk)
    item = object.word_set.all()[page - 1]
    count = object.word_set.count()

    if request.method == 'POST':
        form = WordnetEvaluationForm(request.POST)
        if form.is_valid():
            update_wordnet_evaluation(request.user, form)
            return conditional_redirect(page, count, 'judge-wordnet-item', 'judge-wordnet-done', {'pk': pk})

    context = get_judge_item_context(page, count, 'judge-wordnet-item', [object.pk, page-1])
    context['item'] = item
    context['evaluation'] = models.WordnetEvaluation.objects.filter(judge=request.user, word=item).first()

    return render(request, template_name, context)


def judge_wiki_item(request, pk, page):
    template_name = 'nfo/judge/wiki_item.html'
    object = models.Dataset.objects.get(pk=pk)
    item = object.recipe_set.all()[page - 1]
    count = object.recipe_set.count()

    if request.method == 'POST':
        form = WikiEvaluationForm(request.POST)
        if form.is_valid():
            update_wiki_evaluation(request.user, form)
            return conditional_redirect(page, count, 'judge-wiki-item', 'judge-wiki-done', {'pk': pk})

    context = get_judge_item_context(page, count, 'judge-wiki-item', [object.pk, page-1])
    context['item'] = item
    context['evaluation'] = models.WikiEvaluation.objects.filter(judge=request.user, recipe=item).first()

    return render(request, template_name, context)


def judge_tabel_item(request, pk, page):
    template_name = 'nfo/judge/tabel_item.html'
    object = models.Dataset.objects.get(pk=pk)
    item = object.recipe_set.all()[page - 1]
    count = object.recipe_set.count()

    if request.method == 'POST':
        form = TabelEvaluationForm(request.POST)
        if form.is_valid():
            update_tabel_evaluation(request.user, form)
            return conditional_redirect(page, count, 'judge-tabel-item', 'judge-tabel-done', {'pk': pk})

    context = get_judge_item_context(page, count, 'judge-tabel-item', [object.pk, page-1])
    context['item'] = item
    context['evaluation'] = models.TabelEvaluation.objects.filter(judge=request.user, recipe=item).first()
    context['form'] = TabelEvaluationForm({'correct_categories': get_correct_categories(context['evaluation'])})
    
    return render(request, template_name, context)


def get_correct_categories(evaluation):
    if evaluation:
        return [c.pk for c in evaluation.correct_categories.all()]
    else:
        return []


def get_judge_item_context(page, count, item_url_name, args):
    context = dict()
    context['page'] = page
    context['count'] = count
    context['progress'] = 100 * page / count
    context['previous_url'] = reverse(item_url_name, args=args)
    return context


def conditional_redirect(page, count, item_url_name, done_url_name, kwargs):
    if page < count:
        return redirect(item_url_name, page=page + 1, **kwargs)
    else:
        return redirect(done_url_name, **kwargs)
