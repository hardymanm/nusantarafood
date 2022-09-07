from django.db import transaction
import json
import re
from django.conf import settings
from nfo import models

with open(settings.BASE_DIR / 'stopwords.txt', 'r') as f:
    stopwords_str = f.read()
    stopwords = stopwords_str.splitlines()


def clean_title(title):
    title = title.lower()  # lowercase
    words = re.findall('[A-Za-z]+', title)  # alphabet only
    clean = filter(lambda w: w not in stopwords, words)  # remove stopwords
    return ' '.join(clean)


def get_by_keys(input_dict, keys):
    for key in keys:
        if key in input_dict.keys():
            return input_dict[key]

    raise Exception('Keyerror:', ','.join(keys))


def flatten_list(contents):
    output = []
    if type(contents) == list:
        for content in contents:
            output += flatten_list(content)

    else:
        content = contents.strip()
        if len(content):
            output.append(content)

    return output


class DatasetUtils:
    @staticmethod
    def from_file(f):
        with transaction.atomic():
            dataset = models.Dataset(name=f.name, source=f.name, stopwords=stopwords_str)
            dataset.save()

            lines = f.read()
            documents = []
            for line in lines.splitlines():
                data = json.loads(line)
                title = get_by_keys(data, ['title', 'list_item_title', 'Page_title', 'Page_Title'])
                title_clean = clean_title(title)
                url = get_by_keys(data, ['list_item_url', 'link', 'URL'])
                content = get_by_keys(data, ['page_description', 'Page_description'])  # tree with depth of 1 (Each element is a paragraph)
                content = flatten_list(content)  # combine paragraphs into a string.
                content = '. '.join(content)

                document = models.Document(dataset=dataset, title=title, title_clean=title_clean, url=url, content=content)
                documents.append(document)

            return models.Document.objects.bulk_create(documents)
