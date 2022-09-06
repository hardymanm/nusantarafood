import json
from django.db import models
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult
from celery.result import AsyncResult

from nfo import tasks

DEFAULT_LDA_NUM_TOPIC = 7
DEFAULT_LDA_PASSES = 20


class StopwordTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tabel(models.Model):
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    content = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} / {}'.format(self.name, self.name_en)

    def match(self, title):
        title = title.lower()
        foods = self.content.splitlines()
        for food in foods:
            if food.strip() in title:
                return True

        return False


class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    # LDA model parameter
    stopwords = models.TextField(blank=True, default='')
    num_topics = models.IntegerField(verbose_name="n-Topic", default=DEFAULT_LDA_NUM_TOPIC)
    passes = models.IntegerField(default=DEFAULT_LDA_PASSES)

    # LDA result
    lda_task_id = models.CharField(max_length=255, null=True, blank=True)
    wordnet_task_id = models.CharField(max_length=255, null=True, blank=True)
    wiki_task_id = models.CharField(max_length=255, null=True, blank=True)
    tabel_task_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def run_lda_task(self, stopwords, topic_num, passes):
        self.lda_task_id = tasks.create_lda_model.delay(self.pk, topic_num, passes).id
        self.stopwords = "{}\n{}".format(self.stopwords.strip(), stopwords.strip()).strip()
        self.save()

    def run_wordnet_task(self):
        self.wordnet_task_id = tasks.scrape_wordnet.delay(self.pk).id
        self.save()

    def run_wiki_task(self):
        self.wiki_task_id = tasks.scrape_wiki.delay(self.pk).id
        self.save()

    def run_tabel_task(self):
        self.tabel_task_id = tasks.from_tabel.delay(self.pk).id
        self.save()

    def __get_task(self, task_id):
        result = TaskResult.objects.filter(task_id=task_id)
        if result.exists():
            return result.first()
        elif task_id:
            return {'task_id': task_id, 'status': AsyncResult(task_id).status}
        else:
            return None

    def lda_task(self):
        return self.__get_task(self.lda_task_id)

    def wordnet_task(self):
        return self.__get_task(self.wordnet_task_id)

    def wiki_task(self):
        return self.__get_task(self.wiki_task_id)

    def tabel_task(self):
        return self.__get_task(self.tabel_task_id)

    def stopwords_count(self):
        if self.stopwords:
            return len(self.stopwords.splitlines())
        else:
            return 0


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

    progress = models.IntegerField(default=0)
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
