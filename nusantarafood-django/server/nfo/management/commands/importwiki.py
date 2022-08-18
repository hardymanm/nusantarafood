from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd

from ...models import Recipe

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str, help='input file (.xlsx)')
        parser.add_argument('-d', '--dataset', type=str, help='dataset name')

    def handle(self, *args, **kwargs):
        dataset_name = kwargs['dataset']
        filename = kwargs['input']

        data = pd.read_excel(filename)
        for i, row in data.iterrows():
            title = row['Title']
            recipe = Recipe.objects.get(content__title=title)
            # @todo: update recipe definition from excel file
            