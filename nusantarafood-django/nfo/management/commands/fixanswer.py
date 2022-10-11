import re
from django.core.management.base import BaseCommand

from nfo.models import Document


def clean(title):
    remove_pattern = '[^A-Za-z0-9\- ]'
    return re.sub(remove_pattern, '', title)


class Command(BaseCommand):
    # Only keep alphabets, numbers, dash and space in document title
    # - Document title will affects importwiki
    def handle(self, *args, **kwargs):
        documents = Document.objects.all()
        count = Document.objects.count()
        i = 0
        for document in documents.iterator():
            i += 1
            print('Fixing title... {}/{}'.format(i, count))
            document.title = clean(document.title)
            document.save()
