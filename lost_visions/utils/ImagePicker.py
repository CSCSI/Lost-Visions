import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from random import randint
from django.core import serializers
from lost_visions import models

__author__ = 'ubuntu'


class ImagePicker():
    def __init__(self):
        # saves continually calculating this
        self.image_db_size = models.Image.objects.count()
        print('db size {}'.format(self.image_db_size))

    def get_untagged_image(self, retries=0, allowed_retries=100):
        rand_image_pk = randint(1, self.image_db_size)

        # number_queries = len(connection.queries)
        try:
            an_image = models.Image.objects.get(pk=rand_image_pk)
        except ObjectDoesNotExist:
            retries += 1
            return self.get_untagged_image(retries)

        image_tag_count = models.Tag.objects.filter(image=an_image).count()

        if image_tag_count == 0 and an_image.flickr_id != '':
            # print ('before {} after {} diff {}'.format(number_queries,
            #                                            len(connection.queries),
            #                                            str(len(connection.queries) - number_queries)))
            return str(an_image.flickr_id)

        else:
            print('moving on...')

            if an_image.flickr_id == '':
                print serializers.serialize('json', [an_image, ]) + '\n'

            retries += 1
            print('retries {}'.format(retries))
            if retries > allowed_retries:
                return None

            return self.get_untagged_image(retries=retries)

    def get_untagged_images(self, number):

        image_ids = []
        for i in range(0, int(number)):
            image_ids.append(self.get_untagged_image())
        return image_ids

    def get_tagged_images(self):
        tagged_images = models.Tag.objects.order_by().values_list('image__flickr_id', flat=True).distinct()
        return tagged_images

    def get_tagged_images_for_tag(self, tag):
        pass

    def get_tagged_images_for_tags(self, number, tag_array):
        pass

    def get_tagged_images_for_similar_tag(self, tag):
        pass

    def get_image_from_untagged_cluster(self):
        pass

    def predict_tags_for_image_by_cluster(self):
        pass

image_picker = ImagePicker()

for j in range(0, 1):
    print image_picker.get_untagged_image(1)

    print image_picker.get_untagged_images(3)

    print '\n'

print 'tagged images : '
print image_picker.get_tagged_images()