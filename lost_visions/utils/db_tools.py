import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from random import randint
from django.core import serializers
from django.db.models import Min, Q
from lost_visions import models
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'ubuntu'


def get_next_image_id():

    # min_view_count = models.Image.objects.aggregate(Min('user_count'))
    # min_viewed_image = models.Image.objects.get(user_count=min_view_count['user_count__min'])

    number_of_images = models.Image.objects.count()
    rand_image_pk = randint(1, number_of_images)
# flickr_id=10998459416
    min_viewed_image = models.Image.objects.get(pk=rand_image_pk)
    data = serializers.serialize("json", [min_viewed_image, ])

    print data
    # image_id = str(min_viewed_image.identifier)
    image_id = str(min_viewed_image.id)
    return image_id


def get_info_from_image_model(image_model):
    image_info = dict()
    image_info['imageurl'] = image_model.flickr_medium_source
    if image_info['imageurl'] == '':
        image_info['imageurl'] = image_model.flickr_original_source

    image_info['book_title'] = image_model.title
    image_info['author'] = image_model.first_author
    # image_info['tags'] = image_model.tags1.tags.tag
    return image_info


def get_image_info(image_id):
    try:
        image_for_id = models.Image.objects.get(id=image_id)
        return get_info_from_image_model(image_for_id)

    except ObjectDoesNotExist:
        return None


def read_tsv_file(filename, line_number):

    with open(filename) as f:
        for i, line in enumerate(f):
            if i == line_number:

                words = line.split('\t')
                image = dict()
                image['volume'] = words[0]
                image['publisher'] = words[1]
                image['title'] = words[2]
                image['first_author'] = words[3]
                image['BL_DLS_ID'] = words[4]
                image['pubplace'] = words[5]
                image['book_identifier'] = words[6]
                image['ARK_id_of_book'] = words[7]
                image['date'] = words[8]
                image['flickr_url'] = words[9]
                image['image_idx'] = words[10]
                image['page'] = words[11]
                image['flickr_id'] = words[12]
                image['flickr_small_source'] = words[13]
                image['flickr_small_height'] = words[14]
                image['flickr_small_width'] = words[15]
                image['flickr_medium_source'] = words[16]
                image['flickr_medium_height'] = words[17]
                image['flickr_medium_width'] = words[18]
                image['flickr_large_source'] = words[19]
                image['flickr_large_height'] = words[20]
                image['flickr_large_width'] = words[21]
                image['flickr_original_source'] = words[22]
                image['flickr_original_height'] = words[23]
                image['flickr_original_width'] = words[24]

                f.close()
                return image
        # Reached end of file without hitting line number
        # Close it and return None
        f.close()
        return None


def tests():
    # 2207933

    # image_set = models.Image.objects.filter(book_identifier=2207933)
    #
    # for image in image_set:
    #     print image.date + ' : ' + image.flickr_id
    #     print image.flickr_url
    #
    #     print '*****\n'
    #
    # image_set = models.Image.objects.exclude(volume=0)
    #
    # for image in image_set:
    #     print image.date + ' : ' + image.flickr_id
    #     print image.flickr_url
    #     print image.book_identifier
    #
    #     print '*****'
    # print len(image_set)
    # print '\n***********\n'

    image_set = models.Image.objects.filter(id='9353')

    for image in image_set:
        print image.date + ' : ' + image.flickr_id
        print image.title

        print image.flickr_url
        print image.flickr_medium_source
        print image.book_identifier

        print '*****\n'

    # image_set = models.Image.objects.filter(book_identifier='')
    # for image in image_set:
    #     print image.id
    #     print image
    #
    #     print '*****'
    # print len(image_set)










