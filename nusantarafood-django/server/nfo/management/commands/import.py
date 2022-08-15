from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Dataset, Site, SiteContent

from ...utils.jl_file import JlFile


def create_site_contents(site, contents):
    return [SiteContent(
            site=site,
            title=content['title'],
            url=content['url'],
            content=content['content']) for content in contents]
    

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str,
                            help='input file (.jl file)')
        parser.add_argument('-s', '--site-name', type=str, help='site name')
        parser.add_argument('-d', '--dataset', type=str, help='dataset name')

    def handle(self, *args, **kwargs):
        print(kwargs)
        name = kwargs['site_name']
        dataset_name = kwargs['dataset']
        contents = JlFile.load(kwargs['input'])
        
        with transaction.atomic():
            site, _ = Site.objects.get_or_create(name=name)
            site_contents = SiteContent.objects.bulk_create(create_site_contents(site, contents))
            
            dataset, _ = Dataset.objects.get_or_create(name=dataset_name)
            for c in site_contents:
                dataset.contents.add(c)
        
