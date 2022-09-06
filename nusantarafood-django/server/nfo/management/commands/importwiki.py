import json
from django.core.management.base import BaseCommand
from django.db import transaction

from pathlib import Path
import pandas as pd

from nfo import models


def parse_list(jsonlike_list):
    json_list = jsonlike_list.replace("'", '"')
    return json.loads(json_list)


def get_categories(json_list):
    categories = []
    categories_list = parse_list(json_list)
    for category in categories_list:
        obj, _ = models.FoodCategory.objects.get_or_create(name=category)
        categories.append(obj)

    return categories


def not_found_to_null(definition):
    if definition.lower().strip() == 'not found':
        return None
    else:
        return definition


def update_document(row_data):
    # Include duplicate title
    documents = models.Document.objects.filter(title__iexact=row_data['Title']).all()
    for document in documents:
        document.definition_id = not_found_to_null(row_data['Def_IND'])
        document.definition_ms = not_found_to_null(row_data['Def_MS'])
        document.definition_en = not_found_to_null(row_data['Def_ENG'])
        document.save()
        document.dataset.save()


def import_xlsx_files(file_paths):
    for n, p in enumerate(file_paths):
        print('Processing: ({}/{}) {}'.format(n + 1, len(file_paths), p.as_posix()))
        data = pd.read_excel(p)

        with transaction.atomic():
            for i, row in data.iterrows():
                update_document(row)


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
