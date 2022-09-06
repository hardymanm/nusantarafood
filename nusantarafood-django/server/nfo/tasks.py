import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from nfo import models
from nfo.utils import wordnet
from nfo.utils.lda import Lda

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
    pass


@shared_task(track_started=True)
def from_tabel(dataset_id):
    pass


def get_dataset_stopwords(dataset):
    if type(dataset.stopwords) == str:
        return dataset.stopwords.splitlines()
    else:
        return []
