from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from nfo import forms, models


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


class DatasetLdaDetail(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/dataset/dataset_lda.html'


class DocumentDetail(LoginRequiredMixin, DetailView):
    model = models.Document
    template_name = 'nfo/dataset/document_detail.html'


class JudgeWordnetList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/wordnet_list.html'

    def get_queryset(self):
        return self.model.objects.annotate(Count('word')).filter(word__count__gt=0).all()


class JudgeWordnetInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wordnet_instruction.html'


class JudgeWordnetDone(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wordnet_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = finish_session(models.WordnetSession, self.request, context['object'])
        return context


class JudgeWordnetItem(LoginRequiredMixin, ListView):
    model = models.Word
    paginate_by = 1
    template_name = 'nfo/judge/wordnet_item.html'

    def get_queryset(self):
        dataset_pk = self.kwargs['pk']
        return self.model.objects.filter(dataset__pk=dataset_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        context['progress'] = 100 * context['page_obj'].number / context['paginator'].num_pages
        context['object'] = context['page_obj'][0]
        context['answer'] = models.WordnetAnswer.objects.filter(word=context['object'], judge=self.request.user).first()

        dataset = models.Dataset.objects.get(pk=self.kwargs['pk'])
        update_session(models.WordnetSession, self.request, dataset)
        return context


def update_wordnet_answer(request, pk):
    if request.method == 'POST':
        form = forms.WordnetAnswerForm(request.POST)
        next_url = request.POST.get('next_url')
        if form.is_valid():
            word = models.Word.objects.get(pk=pk)
            answer, _ = models.WordnetAnswer.objects.get_or_create(word=word, judge=request.user, dataset=word.dataset)
            answer.correct_hypernym = form.cleaned_data['correct_hypernym']
            answer.save()
            return redirect(next_url)


class JudgeWikiList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/wiki_list.html'


class JudgeWikiInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_instruction.html'


class JudgeWikiDone(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = finish_session(models.WikiSession, self.request, context['object'])
        return context


class JudgeWikiItem(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 1
    template_name = 'nfo/judge/wiki_item.html'

    def get_queryset(self):
        dataset_pk = self.kwargs['pk']
        return self.model.objects.filter(dataset__pk=dataset_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        context['progress'] = 100 * context['page_obj'].number / context['paginator'].num_pages
        context['object'] = context['page_obj'][0]
        context['answer'] = models.WikiAnswer.objects.filter(document=context['object'], judge=self.request.user).first()

        dataset = models.Dataset.objects.get(pk=self.kwargs['pk'])
        update_session(models.WikiSession, self.request, dataset)
        return context


def update_wiki_answer(request, pk):
    if request.method == 'POST':
        form = forms.WikiAnswerForm(request.POST)
        next_url = request.POST.get('next_url')
        if form.is_valid():
            document = models.Document.objects.get(pk=pk)
            answer, _ = models.WikiAnswer.objects.get_or_create(document=document, judge=request.user, dataset=document.dataset)
            answer.suggested_categories = form.cleaned_data['suggested_categories']
            answer.save()
            return redirect(next_url)


class JudgeTabelList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/tabel_list.html'


class JudgeTabelInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_instruction.html'


class JudgeTabelDone(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = finish_session(models.TabelSession, self.request, context['object'])
        return context


class JudgeTabelItem(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 1
    template_name = 'nfo/judge/tabel_item.html'

    def get_queryset(self):
        dataset_pk = self.kwargs['pk']
        return self.model.objects.filter(dataset__pk=dataset_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        context['progress'] = 100 * context['page_obj'].number / context['paginator'].num_pages
        context['object'] = context['page_obj'][0]
        context['answer'] = models.TabelAnswer.objects.filter(document=context['object'], judge=self.request.user).first()
        context['form'] = forms.TabelAnswerForm({'correct_categories': get_correct_categories(context['answer'])})
        
        dataset = models.Dataset.objects.get(pk=self.kwargs['pk'])
        update_session(models.TabelSession, self.request, dataset)
        return context


def update_tabel_answer(request, pk):
    if request.method == 'POST':
        form = forms.TabelAnswerForm(request.POST)
        next_url = request.POST.get('next_url')
        if form.is_valid():
            document = models.Document.objects.get(pk=pk)
            answer, _ = models.TabelAnswer.objects.get_or_create(document=document, judge=request.user, dataset=document.dataset)
            answer.suggested_categories = form.cleaned_data['suggested_categories']
            answer.correct_categories.set(form.cleaned_data['correct_categories'])
            answer.save()
            return redirect(next_url)


def update_session(session_cls, request, dataset):
    session, _ = session_cls.objects.get_or_create(judge=request.user, dataset=dataset)
    session.dataset_name = dataset.name
    session.judge_username = request.user.username
    session.continue_url = '{}?page={}'.format(request.path, request.GET.get('page', ''))
    session.save()


def finish_session(session_cls, request, dataset):
    session = session_cls.objects.get(judge=request.user, dataset=dataset)
    session.is_finished = True
    session.save()


def get_correct_categories(answer):
    if answer:
        return [c.pk for c in answer.correct_categories.all()]
    else:
        return []
