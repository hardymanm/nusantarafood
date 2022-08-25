import json
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings


class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    # LDA model parameter
    stopwords = models.TextField(null=True, blank=True)
    num_topics = models.IntegerField(verbose_name="n-Topic", default=7)
    passes = models.IntegerField(default=20)

    # LDA result
    lda_data = models.TextField(null=True, blank=True)
    
    run_wiki_at = models.DateTimeField(null=True, default=None)
    run_tabel_at = models.DateTimeField(null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    title_clean = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()

    # wikipedia definition
    definition_id = models.TextField(null=True, blank=True)
    definition_ms = models.TextField(null=True, blank=True)
    definition_en = models.TextField(null=True, blank=True)

    # tabel 1981 category
    generated_categories = models.ManyToManyField('nfo.FoodCategory', related_name='generated_categories', related_query_name='generated_category')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Word(models.Model):
    dataset = models.ForeignKey("nfo.Dataset", on_delete=models.CASCADE)
    noun = models.CharField(max_length=255)
    hypernym = models.TextField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.noun

    def hypernyms(self):
        return json.loads(self.hypernym)


class FoodCategory(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'food categories'


class SessionMixin(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', null=True, on_delete=models.SET_NULL)
    dataset_name = models.CharField(max_length=255, null=True, blank=True)

    judge = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    judge_username = models.CharField(max_length=255, null=True, blank=True)

    is_finished = models.BooleanField(default=False)
    continue_url = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WordnetSession(SessionMixin):
    pass


class WikiSession(SessionMixin):
    pass


class TabelSession(SessionMixin):
    pass


class AnswerMixin(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', null=True, on_delete=models.SET_NULL)  # to simplify query
    judge = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WordnetAnswer(AnswerMixin):
    word = models.ForeignKey('nfo.Word', on_delete=models.CASCADE)
    correct_hypernym = models.CharField(max_length=255, null=True, blank=True)


class WikiAnswer(AnswerMixin):
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    suggested_categories = models.TextField(null=True, blank=True)


class TabelAnswer(AnswerMixin):
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='correct_categories', related_query_name='correct_category', blank=True)
    suggested_categories = models.TextField(null=True, blank=True)
