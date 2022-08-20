from django.core.management.base import BaseCommand
from django.db import transaction

from ...utils.wiki import get_wiki_summary

from ...utils.clean_text import clean_title
from ...models import Dataset


def has_description(recipe):
    if len(recipe.definition_id) > 0:
        return True
    elif len(recipe.definition_ms) > 0:
        return True
    elif len(recipe.definition_en) > 0:
        return True

    return False


class Command(BaseCommand):
    # Command to fills Recipe records (definition_id, definition_ms, definition_en) using Wikipedia.
    # Run commands with 
    # $ python manage.py scrapewiki aziekitchen_ayam --skip
    # where:
    # aziekitchen_ayam  is the dataset name (which existed inside database)
    #                   we will scrape all recipe within this dataset.
    # --skip            skip recipe which already have description in any id, ms or en description
    
    def add_arguments(self, parser):
        parser.add_argument('dataset_name', nargs=1, type=str)
        parser.add_argument('-s', '--skip', action='store_true', help='skip recipe with summary', default=False)
        parser.add_argument('-d', '--default', type=str, help='default summary if empty', default='Not found')

    def handle(self, *args, **kwargs):
        name = kwargs.get('dataset_name')[0]
        default_summary = kwargs['default']
        skip = kwargs['skip']

        dataset = Dataset.objects.get(name=name)
        count = dataset.recipe_set.count()

        for i, recipe in enumerate(dataset.recipe_set.all()):
            print('{}/{} -- {}'.format(i+1, count, recipe))
            if skip and has_description(recipe):
                print('Skip')
                continue

            recipe.title = clean_title(recipe.content.title)
            recipe.definition_id = get_wiki_summary(recipe.title, 'id', default_summary)
            recipe.definition_ms = get_wiki_summary(recipe.title, 'ms', default_summary)
            recipe.definition_en = get_wiki_summary(recipe.title, 'en', default_summary)
            recipe.save()