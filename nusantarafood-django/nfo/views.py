from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView

from nfo import models, forms
from nfo.utils.dataset_utils import DatasetUtils
from nfo.utils.import_utils import import_lda_data, import_lda_terms
from nfo.utils.wiki_utils import WikiUtils


# -- Mixins
class JudgeItemMixin(ListView):
    paginate_by = 1
    method = ''

    def get_queryset(self):
        dataset_pk = self.kwargs['pk']
        return self.model.objects.filter(dataset__pk=dataset_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = update_judge_item_context(self, context)
        update_session(self, context)
        return context


class JudgeDoneMixin(DetailView):
    method = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = finish_session(self, context['object'])
        return context


# --

def home(request):
    return render(request, 'nfo/home.html', {})


# -- Manage dataset

class ManageDatasetList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/manage_dataset/list.html'
    ordering = '-created_at'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.UploadDatasetForm()
        context['lda_form'] = forms.UploadDatasetForm()
        context['word_form'] = forms.UploadDatasetForm()
        context['wiki_form'] = forms.UploadWikiForm()
        return context


class ManageDatasetDetail(LoginRequiredMixin, ListView):
    model = models.Document
    paginate_by = 5
    template_name = 'nfo/manage_dataset/detail.html'

    def get_queryset(self):
        return self.model.objects.filter(dataset__pk=self.kwargs['pk']).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = models.Dataset.objects.get(pk=self.kwargs['pk'])
        return context


class ManageDatasetDelete(LoginRequiredMixin, DeleteView):
    model = models.Dataset
    success_url = reverse_lazy('manage-dataset-list')
    template_name = 'nfo/manage_dataset/delete.html'


def upload_dataset(request):
    if request.method == 'POST':
        form = forms.UploadDatasetForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('files'):
                DatasetUtils.from_file(file)
        else:
            print(form.errors.as_json())

    return redirect('manage-dataset-list')


def upload_dataset_wiki(request):
    if request.method == 'POST':
        form = forms.UploadWikiForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('files'):
                WikiUtils.from_file(file)

    return redirect('manage-dataset-list')


def upload_dataset_lda(request):
    if request.method == 'POST':
        form = forms.UploadWikiForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('files'):
                import_lda_data(file)

    return redirect('manage-dataset-list')


def upload_dataset_word(request):
    if request.method == 'POST':
        form = forms.UploadWikiForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('files'):
                import_lda_terms(file)

    return redirect('manage-dataset-list')


class ManageDocumentDetail(LoginRequiredMixin, DetailView):
    model = models.Document
    template_name = 'nfo/manage_dataset/document_detail.html'


class ManageJudgeList(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 5
    template_name = 'nfo/manage_judge/list.html'
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


class ManageJudgeDetail(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 10
    template_name = 'nfo/manage_judge/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = User.objects.get(pk=self.kwargs['pk'])
        return context


# -- Generic Judge Views: WORDNET

class JudgeWordnetList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/wordnet_list.html'

    def get_queryset(self):
        return self.model.objects.annotate(Count('word')).filter(word__count__gt=0).all()


class JudgeWordnetInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wordnet_instruction.html'


class JudgeWordnetItem(LoginRequiredMixin, JudgeItemMixin):
    model = models.Word
    method = models.METHOD_WORDNET
    template_name = 'nfo/judge/wordnet_item.html'


class JudgeWordnetDone(LoginRequiredMixin, JudgeDoneMixin):
    model = models.Dataset
    method = models.METHOD_WORDNET
    template_name = 'nfo/judge/wordnet_done.html'


# -- Generic Judge Views: WIKI

class JudgeWikiList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/wiki_list.html'

    def get_queryset(self):
        return self.model.objects.annotate(Count('document')).filter(document__count__gt=0).all()


class JudgeWikiInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/wiki_instruction.html'


class JudgeWikiItem(LoginRequiredMixin, JudgeItemMixin):
    model = models.Document
    method = models.METHOD_WIKI
    template_name = 'nfo/judge/wiki_item.html'


class JudgeWikiDone(LoginRequiredMixin, JudgeDoneMixin):
    model = models.Dataset
    method = models.METHOD_WIKI
    template_name = 'nfo/judge/wordnet_done.html'


# -- Generic Judge Views: WIKI

class JudgeTabelList(LoginRequiredMixin, ListView):
    model = models.Dataset
    paginate_by = 5
    template_name = 'nfo/judge/tabel_list.html'

    def get_queryset(self):
        return self.model.objects.annotate(Count('document')).filter(document__count__gt=0).all()


class JudgeTabelInstruction(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/judge/tabel_instruction.html'


class JudgeTabelItem(LoginRequiredMixin, JudgeItemMixin):
    model = models.Document
    method = models.METHOD_TABEL
    template_name = 'nfo/judge/tabel_item.html'


class JudgeTabelDone(LoginRequiredMixin, JudgeDoneMixin):
    model = models.Dataset
    method = models.METHOD_TABEL
    template_name = 'nfo/judge/tabel_done.html'


# -- Update Answer views

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


# -- Helper Functions

def update_judge_item_context(view, context):
    context['dataset'] = models.Dataset.objects.get(pk=view.kwargs['pk'])
    context['progress'] = 100 * context['page_obj'].number / context['paginator'].num_pages
    context['object'] = context['page_obj'][0]

    if view.method == models.METHOD_WORDNET:
        context['answer'] = models.WordnetAnswer.objects.filter(word=context['object'], judge=view.request.user).first()
    elif view.method == models.METHOD_WIKI:
        context['answer'] = models.WikiAnswer.objects.filter(document=context['object'], judge=view.request.user).first()
    elif view.method == models.METHOD_TABEL:
        context['answer'] = models.TabelAnswer.objects.filter(document=context['object'], judge=view.request.user).first()
        context['form'] = forms.TabelAnswerForm({'correct_categories': get_correct_categories(context['answer'])})

    return context


def update_session(view, context):
    request = view.request
    dataset, progress = context['dataset'], context['progress']

    session, _ = models.JudgeSession.objects.get_or_create(method=view.method, judge=request.user, dataset=dataset)
    session.dataset_name = dataset.name
    session.judge_username = request.user.username
    session.continue_url = '{}?page={}'.format(request.path, request.GET.get('page', ''))
    session.progress = progress
    session.save()


def finish_session(view, dataset):
    session = models.JudgeSession.objects.get(judge=view.request.user, method=view.method, dataset=dataset)
    session.is_finished = True
    session.finished_at = timezone.now()
    session.save()
    return session


def get_correct_categories(answer):
    if answer:
        return [c.pk for c in answer.correct_categories.all()]
    else:
        return []
