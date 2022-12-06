import json
import re

from django.db import models
from django.db.models import Q

METHOD_WORDNET = 'wordnet'
METHOD_WIKI = 'wiki'
METHOD_TABEL = 'tabel'


class TokenList(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} ({} lines)'.format(self.name, len(self.content.splitlines()))


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Variation(models.Model):
    ingredient = models.ForeignKey('nfo.Ingredient', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} === {}'.format(self.ingredient.name, self.name)


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

    # @todo: keep the document count but limit documents obj with [:100] for visualization
    def get_tabel_ontology(self):
        context = {'food_categories': [], 'documents': Document.objects.filter(dataset=self).all()}

        categories = FoodCategory.objects.all()
        for category in categories:
            documents = Document.objects.filter(dataset=self).all()
            context['food_categories'].append({'pk': category.pk, 'name': category.name_en, 'documents': [{'pk': document.pk, 'title': document.title} for document in documents]})

        user_categories = dict()
        for document in context['documents']:
            answers = document.tabelanswer_set.all()
            suggested_categories = []
            tmp = [ans.suggested_categories for ans in answers]
            for categories in tmp:
                suggested_categories += re.findall(r'\w+', categories)

            for category in suggested_categories:
                if category in user_categories:
                    user_categories[category].append({'pk': document.pk, 'title': document.title})
                else:
                    user_categories[category] = [{'pk': document.pk, 'title': document.title}]

        context['suggested_categories'] = []
        for category, documents in user_categories.items():
            context['suggested_categories'].append({'name': category, 'documents': documents})

        return context

    def get_wiki_ontology(self):
        context = {'food_categories': [], 'documents': Document.objects.filter(wikianswer__dataset=self)}

        user_categories = dict()
        for document in context['documents']:
            answers = document.wikianswer_set.all()
            suggested_categories = []
            tmp = [ans.suggested_categories for ans in answers]
            for categories in tmp:
                suggested_categories += re.findall(r'\w+', categories)

            for category in suggested_categories:
                if category in user_categories:
                    user_categories[category].append({'pk': document.pk, 'title': document.title})
                else:
                    user_categories[category] = [{'pk': document.pk, 'title': document.title}]

        context['suggested_categories'] = []
        for category, documents in user_categories.items():
            context['suggested_categories'].append({'name': category, 'documents': documents})

        return context


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

    def has_generated_categories(self):
        return self.generated_categories.count() > 0


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

    def get_wordnet_accuracy(self):
        max_score = 0
        score = 0
        for word in self.dataset.word_set.all():
            if WordnetAnswer.objects.filter(word=word, judge=self.judge, dataset__isnull=False).exists():
                answer = WordnetAnswer.objects.filter(word=word, judge=self.judge, dataset__isnull=False).first()
                if answer.correct_hypernym and len(answer.correct_hypernym.strip()) > 0:
                    max_score += 1
                    if answer.correct_hypernym in [h['name'] for h in word.hypernyms()]:
                        score += 1

        return score, max_score

    def print_wordnet_accuracy(self):
        if self.wordnetaccuracy_set.exists():
            return self.wordnetaccuracy_set.first().score

        score, total = self.get_wordnet_accuracy()
        percentage = score / total * 100

        accuracy = WordnetAccuracy(judge_session=self, score='{:.2f}/{} ({:.2f}%)'.format(score, total, percentage))
        accuracy.save()

        return '{}/{} ({:.2f}%)'.format(score, total, percentage)

    def get_wiki_accuracy(self):
        qs = Document.objects.filter(dataset=self.dataset)
        qs = qs.filter(Q(definition_en__regex='^.+$') | Q(definition_id__regex='^.+$') | Q(definition_ms__regex='^.+$'))
        qs = qs.filter(wikianswer__judge=self.judge, wikianswer__suggested_categories__regex='^.+$')

        return qs.count()

    def print_wiki_accuracy(self):
        score = self.get_wiki_accuracy()
        total = self.dataset.document_set.filter(wikianswer__judge=self.judge, wikianswer__suggested_categories__regex='^.+$').count()
        percentage = score / total * 100
        return '{}/{} ({:.2f}%)'.format(score, total, percentage)

    def get_tabel_accuracy(self):
        max_score = 0.0
        score = 0.0
        for document in self.dataset.document_set.all():
            if not document.has_generated_categories():
                continue

            else:
                max_score += 1.0
                answer = TabelAnswer.objects.filter(document=document, judge=self.judge, dataset__isnull=False).first()
                if answer:
                    if answer.has_suggestion() and answer.has_correct_categories():
                        score += 1.0
                    elif answer.has_correct_categories():
                        score += answer.correct_categories.count() / document.generated_categories.count()

        return score, max_score

    def print_tabel_accuracy(self):
        if self.tabelaccuracy_set.exists():
            return self.tabelaccuracy_set.first().score

        score, total = self.get_tabel_accuracy()
        percentage = score / total * 100

        accuracy = TabelAccuracy(judge_session=self, score='{:.2f}/{} ({:.2f}%)'.format(score, total, percentage))
        accuracy.save()

        return '{:.2f}/{} ({:.2f}%)'.format(score, total, percentage)


# Model to cache result
class WordnetAccuracy(models.Model):
    judge_session = models.ForeignKey('nfo.JudgeSession', on_delete=models.CASCADE)
    score = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.judge_session)


class TabelAccuracy(models.Model):
    judge_session = models.ForeignKey('nfo.JudgeSession', on_delete=models.CASCADE)
    score = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.judge_session)


class AnswerMixin(models.Model):
    dataset = models.ForeignKey('nfo.Dataset', null=True, on_delete=models.SET_NULL)  # to simplify query
    judge = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WordnetAnswer(AnswerMixin):
    word = models.ForeignKey('nfo.Word', on_delete=models.CASCADE)
    correct_hypernym = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '#{} Dataset#{} Doc#{} Judge#{},{} word: {}, answer: {}'.format(self.pk, self.word.dataset_id, self.word_id, self.judge_id, self.judge.username, self.word, self.correct_hypernym)


class WikiAnswer(AnswerMixin):
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    suggested_categories = models.CharField(max_length=1000, blank=True, default='', help_text='Pisahkan kategori dengan spasi/separate category with space')

    def __str__(self):
        return '#{} Dataset#{} Doc#{} Judge#{},{}'.format(self.pk, self.document.dataset_id, self.document_id, self.judge_id, self.judge.username)


class TabelAnswer(AnswerMixin):
    document = models.ForeignKey('nfo.Document', on_delete=models.CASCADE)
    correct_categories = models.ManyToManyField('nfo.FoodCategory', related_name='tabel_answer', related_query_name='tabel_answer', blank=True)
    suggested_categories = models.CharField(max_length=1000, blank=True, default='', help_text='Pisahkan kategori dengan spasi/separate category with space')

    def __str__(self):
        return '#{} Dataset#{} Doc#{} Judge#{},{}'.format(self.pk, self.document.dataset_id, self.document_id, self.judge_id, self.judge.username)

    def has_suggestion(self):
        return len(self.suggested_categories.strip()) > 0

    def has_correct_categories(self):
        return self.correct_categories.count() > 0
