import json
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Document(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()

    def __str__(self):
        return self.url


class Dataset(models.Model):
    name = models.CharField(max_length=255)
    documents = models.ManyToManyField('nfo.Document', through='nfo.Recipe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FoodCategory(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'food categories'


class Recipe(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', on_delete=models.CASCADE)
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)

    # wikipedia definition
    definition_id = models.TextField(null=True, blank=True)
    definition_ms = models.TextField(null=True, blank=True)
    definition_en = models.TextField(null=True, blank=True)

    # tabel 1981 category
    generated_categories = models.ManyToManyField('nfo.FoodCategory', related_name='generated_categories', related_query_name='generated_category')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.title)


# LDA & WordNet
class LdaModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    dataset = models.ForeignKey("nfo.Dataset", on_delete=models.CASCADE)
    stopwords = models.TextField()
    num_topics = models.IntegerField(verbose_name="n-Topic")
    passes = models.IntegerField(default=20)

    class Meta:
        verbose_name = 'LDA model'


class Word(models.Model):
    lda_model = models.ForeignKey("nfo.LdaModel", on_delete=models.CASCADE)
    noun = models.CharField(max_length=255)
    hypernym = models.TextField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.noun

    def hypernyms(self):
        return json.loads(self.hypernym)


# Tabel 1981
class TabelEvaluation(models.Model):
    judge = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='correct_categories', related_query_name='correct_category', blank=True)
    suggested_categories = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Tabel judge:{} recipe:{} resp:{}'.format(self.judge.pk, self.recipe.pk, self.suggested_categories)


# Wikipedia
class WikiEvaluation(models.Model):
    judge = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    suggested_categories = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Wiki judge:{} recipe:{} resp:{}'.format(self.judge.pk, self.recipe.pk, self.suggested_categories)


# Wordnet
class WordnetEvaluation(models.Model):
    judge = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    word = models.ForeignKey('nfo.Word', on_delete=models.CASCADE)
    correct_hypernym = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Wordnet judge:{} word:{} resp:{}'.format(self.judge.pk, self.word.pk, self.correct_hypernym)
