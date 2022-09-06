import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from nfo import models
from nfo.utils import wordnet
from nfo.utils.lda import Lda
from nfo.utils.wiki import get_wiki_summary

logger = get_task_logger(__name__)

DEFAULT_LANGUAGE = "zsm"
NUM_WORD_OUTPUT = 30


@shared_task(track_started=True)
def create_lda_model(dataset_id, num_topic, passes):
    dataset = models.Dataset.objects.get(pk=dataset_id)
    lda_model = Lda(dataset.document_set.all(), get_dataset_stopwords(dataset))
    return lda_model.run(num_topic, passes)


@shared_task(track_started=True)
def scrape_wordnet(dataset_id):
    dataset = models.Dataset.objects.get(pk=dataset_id)
    lda_task = dataset.lda_task()
    if not hasattr(lda_task, 'result'):
        logger.info('no result')
        return

    lda_data = json.loads(lda_task.result)
    words = lda_data['tinfo']['Term'][:NUM_WORD_OUTPUT]

    word_list_with_hypernyms = [wordnet.scrape_hypernym(word, DEFAULT_LANGUAGE) for word in words]
    with transaction.atomic():
        models.Word.objects.filter(dataset=dataset).delete()
        for w, hypernyms in word_list_with_hypernyms:
            json_hypernyms = json.dumps(hypernyms)
            word, _ = models.Word.objects.get_or_create(dataset=dataset, noun=w, hypernym=json_hypernyms)
            word.save()

    return len(word_list_with_hypernyms)


@shared_task(track_started=True)
def scrape_wiki(dataset_id):
    qs = models.Document.objects.filter(dataset_id=dataset_id)
    count = qs.count()
    documents = qs.all()
    for i, document in enumerate(documents):
        logger.info('{}/{}'.format(i + 1, count))

        # @todo: Different from jupyter notebook (ipynb). In ipynb, keyword is only first two word of title
        #        Need to ask why later
        keyword = document.title_clean

        document.definition_id = get_wiki_summary(keyword, 'id', '-')
        document.definition_ms = get_wiki_summary(keyword, 'ms', '-')
        document.definition_en = get_wiki_summary(keyword, 'en', '-')
        document.save()


@shared_task(track_started=True)
def from_tabel(dataset_id):
    documents = models.Document.objects.filter(dataset_id=dataset_id).all()
    tabels = models.Tabel.objects.all()

    for document in documents:
        document.generated_categories.clear()
        for tabel in tabels:
            if tabel.match(document.title):
                # @todo: Store english or malay category name
                category = get_category_object(tabel.name_en)
                document.generated_categories.add(category)


def get_dataset_stopwords(dataset):
    if type(dataset.stopwords) == str:
        return dataset.stopwords.splitlines()
    else:
        return []


# helper function
def get_category_object(name):
    obj, _ = models.FoodCategory.objects.get_or_create(name=name)
    return obj
