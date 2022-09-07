import json
from django.db import transaction
import pandas as pd

from nfo import models


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
    for document in documents.iterator():
        document.definition_id = not_found_to_null(row_data['Def_IND'])
        document.definition_ms = not_found_to_null(row_data['Def_MS'])
        document.definition_en = not_found_to_null(row_data['Def_ENG'])
        document.save()

        categories = get_by_keys(row_data, ['Category', 'category'])
        categories = get_categories(categories)
        for category in categories:
            document.generated_categories.add(category)


class WikiUtils:
    @staticmethod
    def from_file(file):
        data = pd.read_excel(file)
        with transaction.atomic():
            for i, row in data.iterrows():
                update_document(row)
