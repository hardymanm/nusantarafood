from django.core.management.base import BaseCommand
from django.db import transaction
import wikipedia
from ...models import Dataset


def has_description(recipe):
    if len(recipe.id_description) > 0:
        return True
    elif len(recipe.ms_description) > 0:
        return True
    elif len(recipe.en_description) > 0:
        return True

    return False


def get_wiki_summary(recipe, lang, default_str):
    try:
        wikipedia.set_lang(lang)
        return wikipedia.summary(recipe.content.title, sentences=4)
    except wikipedia.PageError:
        print('Not found in {}.wikipedia'.format(lang))
        return default_str


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('dataset_name', nargs=1, type=str)
        parser.add_argument('-s', '--skip', action='store_true', help='skip recipe with summary')
        parser.add_argument('-d', '--default', type=str, help='default string if empty')

    def handle(self, *args, **kwargs):
        name = kwargs.get('dataset_name')[0]
        default_str = kwargs.get('default', 'Not found')
        skip = kwargs['skip']
        dataset = Dataset.objects.get(name=name)

        count = dataset.recipe_set.count()
        for i, recipe in enumerate(dataset.recipe_set.all()):
            print('{}/{} -- {}'.format(i+1, count, recipe))
            if skip and has_description(recipe):
                print('Skip')
                continue

            recipe.id_description = get_wiki_summary(recipe, 'id', default_str)
            recipe.ms_description = get_wiki_summary(recipe, 'ms', default_str)
            recipe.en_description = get_wiki_summary(recipe, 'en', default_str)
            recipe.save()
