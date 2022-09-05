from celery import shared_task
from celery.utils.log import get_task_logger

from nfo import models
from nfo.utils.lda import Lda

logger = get_task_logger(__name__)


@shared_task(track_started=True)
def create_lda_model(dataset_id, num_topic, passes):
    dataset = models.Dataset.objects.get(pk=dataset_id)
    lda_model = Lda(dataset.document_set.all(), get_dataset_stopwords(dataset))
    return lda_model.run(num_topic, passes)


@shared_task(track_started=True)
def scrape_wordnet(dataset_id):
    pass


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
