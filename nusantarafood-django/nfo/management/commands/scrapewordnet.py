import json

from django.core.management.base import BaseCommand

from nfo import models
from nfo.utils.wordnet_utils import get_hypernyms


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        words = models.Word.objects.all()
        for word in words:
            hypernyms = get_hypernyms(word.noun, 'zsm')
            word.hypernym_json = json.dumps(hypernyms)
            word.save()
