import os
from optparse import make_option

import sys
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from lost_visions.models import ImageCollection, ImageMapping, Image, LostVisionUser


def err(error):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)


class Command(BaseCommand):
    args = '<import_collections an_arg ...>'
    help = 'Imports collections'

    option_list = BaseCommand.option_list + (
        make_option('--log_output',
                    action='store',
                    dest='log_output',
                    default=0,
                    help='Logging level 0-2, increasing detail to stdout. Default is 0'),
        make_option('--list_file',
                    action='store',
                    dest='list_file',
                    default=None,
                    help='File of ImageIDs to import. Required.'),
        make_option('--collection_name',
                    action='store',
                    dest='collection_name',
                    default=None,
                    help='Name of collection. Required.'),
    )

    def handle(self, *args, **options):

        if not options['list_file']:
            raise CommandError('Need a list file'.format())
        if not options['collection_name']:
            raise CommandError('Need a name for the collection.'.format())

        for thing in options:
            try:
                print 'ok', thing, options[thing]
            except:
                raise CommandError('{}'.format(thing))

        anon_user = User.objects.get(username='Anon_y_mouse')
        anon_lv_user = LostVisionUser.objects.get(username=anon_user)
        collection, created = ImageCollection.objects.get_or_create(
            name=options['collection_name'],
            user=anon_lv_user
        )

        mappings = []
        skipped = []

        try:
            with open(options['list_file'], 'r') as list_file:
                for image_id in list_file:
                    image_id = image_id.strip()
                    print '\n*{}*'.format(image_id)

                    try:
                        image = Image.objects.get(flickr_id=image_id)
                        mapping, created = ImageMapping.objects.get_or_create(
                            collection=collection, image=image
                        )
                        if created:
                            mappings.append(mapping)
                        else:
                            skipped.append(mapping)
                    except Exception as e1:
                        print e1
                        err(e1)

        except Exception as e2:
            print e2
            err(e2)

        print mappings
