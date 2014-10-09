import os
import pprint

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
import operator
from django.db.models import Q
from random import randint
from django.core import serializers
from lost_visions import models

__author__ = 'ubuntu'


# can cause multiple db accesses on django models
def pprint_object(obj):
    print pprint.pformat(obj, indent=1, width=80, depth=None)


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
        tagged_images = models.Tag.objects.filter(tag=tag).order_by().values_list('image__flickr_id', flat=True).distinct()
        return tagged_images

    def get_tagged_images_for_tags(self, tag_array, and_or='or', number=None):

        # only interested in images where all tags are present
        if and_or is 'and':

            # For each tag find the Tag DB objects with that tag
            tagged_images = dict()
            for tag in tag_array:
                tagged_images[tag] = (self.get_tagged_images_for_tag(tag))

            # pprint_object(tagged_images)

            # find largest list.
            # If the tag isn't in this, there's no reason looking in the others
            largest_list = []
            most_used_tag = ''
            for key_tag in tagged_images:
                if len(tagged_images[key_tag]) > len(largest_list):
                    largest_list = tagged_images[key_tag]
                    most_used_tag = key_tag

            # traverse the longest list, compare with others
            images_with_all_tags = []
            for image_in_largest_list in largest_list:
                tags_lists_image_appears_in = 0
                for key_tag in tagged_images:
                    # If the inspected list B is not the longest list A (pointless comparing A and A)
                    # and the image we're looking at from A is also in list B
                    if key_tag is not most_used_tag and image_in_largest_list in tagged_images[key_tag]:
                        # Increment the number of times we've seen it
                        tags_lists_image_appears_in += 1

                # If we say the image N-1 times, it was in every list
                # N-1 as we didn't search the longest list
                if tags_lists_image_appears_in == len(tag_array) - 1:
                    # Add image to return list
                    images_with_all_tags.append(image_in_largest_list)

            return images_with_all_tags

        # assume 'or', so any one of the given tags gives a hit
        else:
            # 'reduce' the input list to a long list of "OR"s and filter for all
            tagged_images = models.Tag.objects.filter(reduce(operator.or_, (Q(tag=x) for x in tag_array))).order_by().values_list('image__flickr_id', flat=True).distinct()

        return list(set(tagged_images))

    def get_tagged_images_for_similar_tag(self, tag):
        pass

    def get_image_from_untagged_cluster(self):
        pass

    def predict_tags_for_image_by_cluster(self):
        pass

image_picker = ImagePicker()

# for j in range(0, 1):
#     print image_picker.get_untagged_image(1)
#
#     print image_picker.get_untagged_images(3)
#
#     print '\n'

print 'tagged images : '

number_queries = len(connection.queries)

print image_picker.get_tagged_images_for_tags(['man', 'woman'], and_or='or')



print ('before {} after {} diff {}'.format(number_queries,
                                           len(connection.queries),
                                           str(len(connection.queries) - number_queries)))
qus = len(connection.queries) - number_queries
print connection.queries[:(qus * -1)]

pprint_object(connection.queries)
