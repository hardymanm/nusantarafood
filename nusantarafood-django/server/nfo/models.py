from django.db import models


class Judge(models.Model):
    name = models.CharField(max_length=255)


class Site(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name


class SiteContent(models.Model):
    site = models.ForeignKey('nfo.Site', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    
    def __str__(self):
        return '{}: {}'.format(self.site, self.title)


class Dataset(models.Model):
    name = models.CharField(max_length=255)
    contents = models.ManyToManyField('nfo.SiteContent', through='nfo.Recipe')
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)


class FoodCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'food categories'


class Recipe(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', on_delete=models.CASCADE)
    site_content = models.ForeignKey('nfo.SiteContent', on_delete=models.CASCADE)
    
    # wikipedia description
    id_description = models.TextField(blank=True)
    ms_description = models.TextField(blank=True)
    en_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)


# LDA & WordNet
class LdaModel(models.Model):
    name = models.CharField(max_length=255)
    dataset = models.ForeignKey("nfo.Dataset", on_delete=models.CASCADE)
    stopwords = models.TextField()
    topic_count = models.IntegerField(verbose_name="n-Topic")
    iteration = models.IntegerField(default=20)

    class Meta:
        verbose_name = 'LDA model'


class Word(models.Model):
    lda_model = models.ForeignKey("nfo.LdaModel", on_delete=models.CASCADE)
    noun = models.CharField(max_length=255)
    hypernym = models.CharField(max_length=255)


# Tabel 1981
class TabelEvaluation(models.Model):
    judge = models.ForeignKey('nfo.Judge', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    generated_categories = models.ManyToManyField('nfo.FoodCategory',
                                                  related_name='generated_categories',
                                                  related_query_name='generated_category')
    correct_categories = models.ManyToManyField('nfo.FoodCategory',
                                                related_name='correct_categories',
                                                related_query_name='correct_category')
    suggested_categories = models.ManyToManyField('nfo.FoodCategory',
                                                  related_name='judge_tabel_categories',
                                                  related_query_name='judge_tabel_category')
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)


# Wikipedia
class WikiEvaluation(models.Model):
    judge = models.ForeignKey('nfo.Judge', on_delete=models.CASCADE)
    recipe = models.ForeignKey('nfo.Recipe', on_delete=models.CASCADE)
    suggested_categories = models.ManyToManyField('nfo.FoodCategory',
                                                  related_name='judge_wiki_categories',
                                                  related_query_name='judge_wiki_category')
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)
