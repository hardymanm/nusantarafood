from django.core.management.base import BaseCommand

from ...models import Site, SiteContent

from ...utils.jl_file import JlFile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', type=str,
                            help='input file (.jl file)')
        parser.add_argument('-n', '--name', type=str, help='site name')

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        contents = JlFile.load(kwargs['input'])

        site, is_created = Site.objects.get_or_create(name=name)
        site_contents = [SiteContent(
            site=site,
            title=p['title'],
            url=p['url'],
            content=p['content']) for p in contents]
        SiteContent.objects.bulk_create(site_contents)
