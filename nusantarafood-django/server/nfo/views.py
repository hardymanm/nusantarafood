from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse
from django.contrib import messages

from nfo import models
from nfo.forms import WordnetEvaluationForm
from nfo.utils.evaluation import update_wordnet_evaluation


def index(request):
    return render(request, 'nfo/index.html', {})


class JudgeTabelList(ListView):
    model = models.Dataset
    template_name = 'nfo/judge/dataset_tabel.html'


class JudgeWikiList(ListView):
    model = models.Dataset
    template_name = 'nfo/judge/dataset_wiki.html'


class JudgeWordnetList(ListView):
    model = models.LdaModel
    template_name = 'nfo/judge/dataset_wordnet.html'


class JudgeWordnetInstruction(DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/instruction_wordnet.html'


def judge_wordnet_item(request, pk, page):
    model = models.LdaModel
    template_name = 'nfo/judge/judge_wordnet.html'

    if request.method == 'POST':
        form = WordnetEvaluationForm(request.POST)
        if form.is_valid():
            update_wordnet_evaluation(request.user, form)
            return redirect('judge-wordnet-item', pk=pk, page=page + 1)

    object = model.objects.get(pk=pk)
    item = object.word_set.all()[page - 1]
    count = object.word_set.count()
    context = dict()
    context['page'] = page
    context['count'] = count
    context['progress'] = 100 * page / count
    context['previous_url'] = reverse('judge-wordnet-item', args=[object.pk, page - 1])
    context['item'] = item
    context['evaluation'] = models.WordnetEvaluation.objects.filter(judge=request.user, word=item).first()

    return render(request, template_name, context)
