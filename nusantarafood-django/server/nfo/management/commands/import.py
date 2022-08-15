from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Content, Dataset

from ...utils.jl_file import JlFile


def create_site_contents(contents):
    return [Content(
            title=content['title'],
            url=content['url'],
            content=content['content']) for content in contents]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, help='input file (.jl file)')
        parser.add_argument('-d', '--dataset', type=str, help='dataset name')

    def handle(self, *args, **kwargs):
        dataset_name = kwargs['dataset']
        contents = JlFile.load(kwargs['input'])

        with transaction.atomic():
            site_contents = Content.objects.bulk_create(create_site_contents(contents))

            dataset, _ = Dataset.objects.get_or_create(name=dataset_name)
            for c in site_contents:
                dataset.contents.add(c)

# python manage.py import -i /home/amir/Documents/test/assets/jl/aziekitchen-ayam.jl -d aziekitchen_ayam