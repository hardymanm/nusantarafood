import json

from django.db import models

METHOD_WORDNET = 'wordnet'
METHOD_WIKI = 'wiki'
METHOD_TABEL = 'tabel'


class Stopword(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} ({} lines)'.format(self.name, len(self.content.splitlines()))


class Tabel(models.Model):
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    content = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} / {}'.format(self.name, self.name_en)


class Dataset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    # LDA model parameter
    stopwords = models.TextField(blank=True, default='')
    num_topics = models.IntegerField(verbose_name="n-Topic", null=True)
    passes = models.IntegerField(null=True)
    lda_data = models.TextField(blank=True, default='')
    lda_terms = models.TextField(blank=True, default='')

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
    generated_categories = models.ManyToManyField('nfo.FoodCategory', related_name='generated_categories', related_query_name='generated_category', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FoodCategory(models.Model):
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'food categories'


class Word(models.Model):
    dataset = models.ForeignKey("nfo.Dataset", on_delete=models.CASCADE)
    noun = models.CharField(max_length=255)
    hypernym_json = models.TextField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.noun

    def hypernyms(self):
        return json.loads(self.hypernym_json)


METHOD_CHOICES = (
    (METHOD_WORDNET, METHOD_WORDNET),
    (METHOD_WIKI, METHOD_WIKI),
    (METHOD_TABEL, METHOD_TABEL),
)


class JudgeSession(models.Model):
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    dataset = models.ForeignKey('nfo.Dataset', null=True, on_delete=models.SET_NULL)
    dataset_name = models.CharField(max_length=255, null=True, blank=True)

    judge = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    judge_username = models.CharField(max_length=255, null=True, blank=True)

    progress = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    continue_url = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}/{} Done:{} -- {}'.format(self.dataset, self.method.upper(), self.is_finished, self.judge_username)


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
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='wiki_answer', related_query_name='wiki_answer', blank=True)


class TabelAnswer(AnswerMixin):
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='tabel_answer', related_query_name='tabel_answer', blank=True)
