from django.core.management.base import BaseCommand
from django.db import transaction

from pathlib import Path

from ...models import Document, Dataset

from ...utils.jl_file import JlFile


def generate_dataset_name(jl_path):
    return jl_path.name.replace('.jl', '')


def create_document(content):
    return Document(
        title=content['title'],
        url=content['url'],
        content=content['content']
    )


def create_document_list(contents):
    return [create_document(content) for content in contents]


def import_jlfiles(file_paths):
    for p in file_paths:
        dataset_name = generate_dataset_name(p)
        documents = JlFile.load(p.as_posix())

        with transaction.atomic():
            docs = Document.objects.bulk_create(create_document_list(documents))
            dataset, _ = Dataset.objects.get_or_create(name=dataset_name)
            for d in docs:
                dataset.documents.add(d)


class Command(BaseCommand):
    # Command to fill Dataset, Document, and Recipe (partially)
    # Run command with:
    # $ python manage.py importjl /home/amir/assets/jl
    # where:
    # /home/amir/assets/jl   is the input directory containing .jl files
    #                        dataset name will be taken from .jl filename
    #                        eg: aziekitchen_udang (from aziekitchen_udang.jl)
    def add_arguments(self, parser):
        parser.add_argument('input', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        input_file = Path(kwargs['input'][0])
        jl_files = []
        if input_file.is_dir():
            jl_files = list(input_file.glob('*.jl'))
        elif input_file.exists():
            jl_files = [input_file]

        import_jlfiles(jl_files)
