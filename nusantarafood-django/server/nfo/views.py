from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from nfo import models
from nfo.forms import TabelEvaluationForm, WikiEvaluationForm, WordnetEvaluationForm
from nfo.management.commands.wordnet import load_stopwords, make_LDAmodel
from nfo.utils.evaluation import update_tabel_evaluation, update_wiki_evaluation, update_wordnet_evaluation


def index(request):
    return render(request, 'nfo/index.html', {})


class DatasetList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/dataset/dataset_list.html'

class DatasetDetail(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 5
    template_name = 'nfo/dataset/dataset_detail.html'

    def get_queryset(self):
        dataset_pk = self.kwargs['pk']
        return self.model.objects.filter(dataset__pk=dataset_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        return context


class JudgeTabelList(LoginRequiredMixin, ListView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_list.html'


class JudgeTabelInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_instruction.html'


class JudgeTabelDone(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_done.html'


class JudgeWikiList(LoginRequiredMixin, ListView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_list.html'


class JudgeWikiInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_instruction.html'


class JudgeWikiDone(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_done.html'


class JudgeWordnetList(LoginRequiredMixin, ListView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_list.html'


class JudgeWordnetInstruction(LoginRequiredMixin, DetailView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_instruction.html'


class JudgeWordnetDone(LoginRequiredMixin, DetailView):
    model = models.LdaModel
    template_name = 'nfo/judge/wordnet_done.html'


@login_required
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


@login_required
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


@login_required
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


def generate_ldamodel(request):
    model = models.LdaModel.objects.get(pk=3)
    data = model.data
    return render(request, 'nfo/test.html', {'data': data})
    