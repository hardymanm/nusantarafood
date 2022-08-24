from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from nfo import models


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
    template_name = 'wordnet_list.html'
    
    
class JudgeWikiList(LoginRequiredMixin, ListView):
    model = models.Dataset
    template_name = 'wiki_list.html'
    
    
class JudgeTabelList(LoginRequiredMixin, ListView):
    model = models.Dataset
    template_name = 'tabel_list.html'