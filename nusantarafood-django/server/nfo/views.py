from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count

from nfo import forms, models, tasks
from nfo.forms import CreateLdaModelForm
from nfo.utils.dataset_utils import DatasetUtils


def index(request):
    return render(request, 'nfo/index.html', {})


class DatasetList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/manage_dataset/dataset_list.html'
    ordering = '-created_at'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.UploadJlForm()
        return context


class DatasetDetail(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 5
    template_name = 'nfo/manage_dataset/dataset_detail.html'

    def get_queryset(self):
        return self.model.objects.filter(dataset__pk=self.kwargs['pk']).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        context['lda_form'] = CreateLdaModelForm()
        return context


def upload_jlfile(request):
    if request.method == 'POST':
        form = forms.UploadJlForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            DatasetUtils.from_file(file)
        else:
            print('------------------------------')
            print(form.errors.as_json())

    return redirect('dataset-list')


class DatasetDelete(LoginRequiredMixin, DeleteView):
    model = models.Dataset
    success_url = '/dataset'
    template_name = 'nfo/manage_dataset/dataset_delete.html'


class DatasetLdaDetail(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/manage_dataset/dataset_lda.html'


def run_lda_task(request, pk):
    if request.method == 'POST':
        form = CreateLdaModelForm(request.POST)
        if form.is_valid():
            dataset = models.Dataset.objects.get(pk=pk)
            dataset.run_lda_task(form.cleaned_data['stopwords'], form.cleaned_data['topic_num'], form.cleaned_data['passes'])

    return redirect('dataset-detail', pk)


def run_wordnet_task(request, pk):
    dataset = models.Dataset.objects.get(pk=pk)
    dataset.run_wordnet_task()
    return redirect('dataset-detail', pk)


def run_wiki_task(request, pk):
    dataset = models.Dataset.objects.get(pk=pk)
    dataset.run_wiki_task()
    return redirect('dataset-detail', pk)


def run_tabel_task(request, pk):
    dataset = models.Dataset.objects.get(pk=pk)
    dataset.run_tabel_task()
    return redirect('dataset-detail', pk)


class DocumentDetail(LoginRequiredMixin, DetailView):
    model = models.Document
    template_name = 'nfo/manage_dataset/document_detail.html'


class RegexPlayground(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 5
    template_name = 'nfo/regex_playground.html'

    def get_queryset(self):
        form = forms.RegexPlaygroundForm(self.request.GET)
        if form.is_valid():
            return self.model.objects.filter(content__regex=form.cleaned_data['regex']).order_by('-dataset_id')

        return self.model.objects.order_by('-dataset_id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.RegexPlaygroundForm(self.request.GET)
        context['document_count'] = self.model.objects.count()
        return context


class JudgeList(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 5
    template_name = 'nfo/manage_judge/judge_list.html'
    form = forms.AddJudgeForm()

    def get_queryset(self):
        return self.model.objects.filter(groups__name='judge').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        self.form = forms.AddJudgeForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            self.form = forms.AddJudgeForm()  # clear form

        return self.get(request, *args, **kwargs)


class JudgeDetail(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 10
    template_name = 'nfo/manage_judge/judge_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = User.objects.get(pk=self.kwargs['pk'])
        return context


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
        update_session(models.WordnetSession, self.request, dataset, context['progress'])
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
        update_session(models.WikiSession, self.request, dataset, context['progress'])
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
        update_session(models.TabelSession, self.request, dataset, context['progress'])
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


def update_session(session_cls, request, dataset, progress):
    session, _ = session_cls.objects.get_or_create(judge=request.user, dataset=dataset)
    session.dataset_name = dataset.name
    session.judge_username = request.user.username
    session.continue_url = '{}?page={}'.format(request.path, request.GET.get('page', ''))
    session.progress = progress
    session.save()


def finish_session(session_cls, request, dataset):
    session = session_cls.objects.get(judge=request.user, dataset=dataset)
    session.is_finished = True
    session.save()
    return session


def get_correct_categories(answer):
    if answer:
        return [c.pk for c in answer.correct_categories.all()]
    else:
        return []
