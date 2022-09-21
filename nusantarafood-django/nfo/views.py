from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib import messages

from nfo import models, forms
from nfo.utils.dataset_utils import DatasetUtils
from nfo.utils.import_utils import import_lda_data, import_lda_terms
from nfo.utils.wiki_utils import WikiUtils


# -- Utility
def ingredient_dataentry(request):
    if request.method == 'POST':
        form = forms.IngredientForm(request.POST)
        form.save()

    return render(request, 'nfo/utils/ingredient_dataentry.html', {'form': forms.IngredientForm()})


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
        context['rename_form'] = forms.RenameDatasetForm(instance=context['object'])
        context['split_form'] = forms.SplitDatasetForm(instance=context['object'], initial={'name': '{}_part'.format(context['object'].name)})
        context['join_form'] = forms.JoinDatasetForm()
        return context


class ManageDatasetDelete(LoginRequiredMixin, DeleteView):
    model = models.Dataset
    success_url = reverse_lazy('manage-dataset-list')
    template_name = 'nfo/manage_dataset/delete.html'


class ManageDatasetLda(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/manage_dataset/lda.html'


class ManageDatasetWordnetOntology(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/manage_dataset/ontology.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Wordnet Ontology'
        return context


class ManageDatasetWikiOntology(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/manage_dataset/ontology.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.object.get_wiki_ontology())
        context['page_title'] = 'Wiki Ontology'
        return context


class ManageDatasetTabelOntology(LoginRequiredMixin, DetailView):
    model = models.Dataset
    template_name = 'nfo/manage_dataset/ontology.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.object.get_tabel_ontology())
        context['page_title'] = 'Tabel 1981 Ontology'
        return context


def download_wordnet_ontology_json(request, pk):
    pass


def download_wiki_ontology_json(request, pk):
    documents = models.Document.objects.filter(dataset__id=pk).prefetch_related('wikianswer_set__correct_categories')
    return JsonResponse([document_to_dict(d, models.METHOD_WIKI) for d in documents], safe=False)


def download_tabel_ontology_json(request, pk):
    documents = models.Document.objects.filter(dataset__id=pk).prefetch_related('tabelanswer_set__correct_categories')
    return JsonResponse([document_to_dict(d, models.METHOD_TABEL) for d in documents], safe=False)


def rename_dataset(request, pk):
    instance = models.Dataset.objects.get(pk=pk)
    if request.method == 'POST':
        form = forms.RenameDatasetForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()

        else:
            messages.error(request, error_as_ul(form.errors))

    return redirect('manage-dataset-detail', pk=pk)


def split_dataset(request, pk):
    instance = models.Dataset.objects.get(pk=pk)
    if request.method == 'POST':
        form = forms.SplitDatasetForm(request.POST, instance=instance)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            size = form.cleaned_data.get('size')

            with transaction.atomic():
                new_dataset = models.Dataset.objects.create(name=name)
                documents = instance.document_set.order_by('pk')[:size]
                for document in documents:
                    document.dataset = new_dataset
                models.Document.objects.bulk_update(documents, ['dataset'])

                delete_related_judge_sessions(instance)
                delete_related_answers(instance)

        else:
            messages.error(request, error_as_ul(form.errors))

    return redirect('manage-dataset-detail', pk=pk)


def join_dataset(request, pk):
    instance = models.Dataset.objects.get(pk=pk)
    if request.method == 'POST':
        form = forms.JoinDatasetForm(request.POST)
        if form.is_valid():
            datasets = form.cleaned_data.get('datasets')

            with transaction.atomic():
                documents = []
                for dataset in datasets:
                    delete_related_judge_sessions(dataset)
                    delete_related_answers(dataset)
                    documents += dataset.document_set.all()[:]

                for document in documents:
                    document.dataset = instance

                models.Document.objects.bulk_update(documents, ['dataset'])

                for dataset in datasets:
                    dataset.delete()

        else:
            messages.error(request, error_as_ul(form.errors))

    return redirect('manage-dataset-detail', pk=pk)


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


# -- Generic Judge Views: TABEL

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
            answer.correct_categories.set(form.cleaned_data['correct_categories'])
            answer.suggested_categories = form.cleaned_data['suggested_categories']
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
        context['categories'] = models.FoodCategory.objects.order_by('name').all()
        context['answer'] = models.WikiAnswer.objects.filter(document=context['object'], judge=view.request.user).first()
        context['form'] = forms.WikiAnswerForm()
    elif view.method == models.METHOD_TABEL:
        context['categories'] = models.FoodCategory.objects.order_by('name').all()
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


def error_as_ul(form_errors):
    html = '<ul class="mb-0">'
    for key, errors in form_errors.items():
        for error in errors:
            html += '<li>{}</li>'.format(error)
    html += '</ul>'
    return html


def delete_related_judge_sessions(dataset):
    models.JudgeSession.objects.filter(dataset=dataset).delete()


def delete_related_answers(dataset):
    models.WordnetAnswer.objects.filter(dataset=dataset).delete()
    models.WikiAnswer.objects.filter(dataset=dataset).delete()
    models.TabelAnswer.objects.filter(dataset=dataset).delete()


def document_to_dict(document, method):
    if method == models.METHOD_WIKI:
        categories = models.FoodCategory.objects.filter(wiki_answer__document=document).all()
    elif method == models.METHOD_TABEL:
        categories = models.FoodCategory.objects.filter(tabel_answer__document=document).all()
    else:
        categories = []

    return {
        'title': document.title,
        'title_clean': document.title_clean,
        'categories': [c.name_en for c in categories]
    }
