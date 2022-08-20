import json
from django.core.management.base import BaseCommand
from django.db import transaction

from pathlib import Path
import pandas as pd

from nfo.models import Recipe, FoodCategory


def get_by_keys(input_dict, keys):
    for key in keys:
        if key in input_dict.keys():
            return input_dict[key]

    raise Exception('Keyerror:', ','.join(keys))


def parse_list(jsonlike_list):
    json_list = jsonlike_list.replace("'", '"')
    return json.loads(json_list)


def get_categories(json_list):
    categories = []
    categories_list = parse_list(json_list)
    for category in categories_list:
        obj, _ = FoodCategory.objects.get_or_create(name=category)
        categories.append(obj)

    return categories


def update_recipe(row_data):
    # Include duplicate title
    recipes = Recipe.objects.filter(document__title__iexact=row_data['Title']).all()
    for recipe in recipes:
        recipe.title = row_data['Cleaned']
        recipe.definition_id = row_data['Def_IND']
        recipe.definition_ms = row_data['Def_MS']
        recipe.definition_en = row_data['Def_ENG']

        categories = get_by_keys(row_data, ['Category', 'category'])
        categories = get_categories(categories)
        for category in categories:
            recipe.generated_categories.add(category)

        recipe.save()


def import_xlsx_files(file_paths):
    for p in file_paths:
        data = pd.read_excel(p)

        with transaction.atomic():
            for _, row in data.iterrows():
                update_recipe(row)


class Command(BaseCommand):
    # Command to fill Recipe (definitions and category) from ms excel file
    # Run command with:
    # $ python manage.py importwiki /home/amir/assets/wiki
    # where:
    # /home/amir/assets/wiki   is the input directory containing .xlsx file
    def add_arguments(self, parser):
        parser.add_argument('input', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        input_file = Path(kwargs['input'][0])
        xlsx_files = []
        if input_file.is_dir():
            xlsx_files = list(input_file.glob('*.xlsx'))
        elif input_file.exists():
            xlsx_files = [input_file]

        import_xlsx_files(xlsx_files)
