from django.db import models


class Judge(models.Model):
    name = models.CharField(max_length=255)


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
        return '{}: {}'.format(self.dataset.name, self.document.title)


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


# Tabel 1981
class TabelEvaluation(models.Model):
    judge = models.ForeignKey('nfo.Judge', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='correct_categories', related_query_name='correct_category')
    suggested_categories = models.ManyToManyField('nfo.FoodCategory', related_name='judge_tabel_categories', related_query_name='judge_tabel_category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Wikipedia
class WikiEvaluation(models.Model):
    judge = models.ForeignKey('nfo.Judge', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    suggested_categories = models.ManyToManyField('nfo.FoodCategory', related_name='judge_wiki_categories', related_query_name='judge_wiki_category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
