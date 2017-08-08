from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.http.request import HttpRequest

from lost_visions.models import ImageCollection
from lost_visions.views import get_collection_zip_stream


class Command(BaseCommand):
    args = '<zip_collections an_arg ...>'
    help = 'Zips all the collections'

    option_list = BaseCommand.option_list + (
        make_option('--log_output',
                    action='store',
                    dest='log_output',
                    default=0,
                    help='Logging level 0-2, increasing detail to stdout. Default is 0'),

        make_option('--max_files',
                    action='store',
                    dest='max_files',
                    default=None,
                    help='Number of files to do into the zip. BEWARE: Default is all of them.'),
    )

    def handle(self, *args, **options):

        for thing in args:
            try:
                print 'ok', thing
            except:
                raise CommandError('{}'.format(thing))

        for thing in options:
            try:
                print 'ok', thing, options[thing]
            except:
                raise CommandError('{}'.format(thing))

        collections = ImageCollection.objects.all()
        print 'collections.count', collections.count()

        for collection in collections:
            print '\n\n\n'
            req = HttpRequest()
            s, name = get_collection_zip_stream(
                req, collection.id,
                log_output=options['log_output'],
                max_files=options['max_files'])
            print s.len, name
