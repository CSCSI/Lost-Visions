import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import json
from django.db.models import Q
from crowdsource.settings import BASE_DIR, STATIC_URL
from random import randint
from django.core import serializers
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
    image_json = serializers.serialize("json", [image_model, ])
    image_object = json.loads(image_json)
    image_info = image_object[0]['fields']

    image_info['imageurl'] = image_model.flickr_medium_source
    if image_info['imageurl'] == '':
        image_info['imageurl'] = image_model.flickr_original_source

    return image_info


def find_image(image_id):
    web_folder = 'bl_images'
    root_folder = os.path.join(BASE_DIR, 'lost_visions')
    root_folder = os.path.join(root_folder, 'static')
    root_folder = os.path.join(root_folder, web_folder)

    for a_file in os.listdir(root_folder):
        try:
            # image_for_id = models.Image.objects.get(flickr_id=a_file.split('_')[0])
            # if image_for_id:
            #     print 'found' + a_file
            full_path = os.path.join(root_folder, a_file)
            if os.path.isfile(full_path) and a_file.split('_')[0] == image_id:
                image_root_url = os.path.join(STATIC_URL, 'bl_images')
                file_url = os.path.join(image_root_url, a_file)
                return file_url
                # return STATIC_URL + 'bl_images/' + a_file
        except:
            pass
    return None


def get_image_info(image_id):
    arcca_image = find_image(image_id)

    try:
        image_for_id = models.Image.objects.get(flickr_id=image_id)
        image_info = get_info_from_image_model(image_for_id)

        if arcca_image:
            image_info['imageurl'] = arcca_image

        if image_info['imageurl'] == '':
            print 'ERROR with IMAGE_ID = ' + image_id
            return get_image_info(get_next_image_id())
        else:
            image_for_id.views_begun += 1
            image_for_id.save()

            return image_info

    except ObjectDoesNotExist:
        print 'no object in db for ' + image_id
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

    find_me = 'illust'
    image_set = models.Image.objects.filter(Q(title__contains=find_me))

    found = dict()
    number_found = 0
    for image in image_set:
        found[image.title] = image

    stopwords = []

    for image in found:
        try:
            title = found[image].title
            title_split = title.split()
            for index, word in enumerate(title_split):
                if find_me.lower() in word.lower():
                    before = title_split[0:index]
                    after = title_split[index+1:]
                    after_str = ' '.join(after)
                    if 'by' in after_str:
                        for index2, word2 in enumerate(after):
                            if 'by'.lower() in word2.lower():
                                if 'author' in after_str:
                                    print '(author) ' + found[image].first_author

                                print ' '.join(after[index2:])
                                print found[image].title
                                print '\n'
                                number_found += 1

            # split_title = found[image].title.lower().split(find_me.lower())
            # before = split_title[0].split()
            # after = split_title[1].split()

            # if after[0] not in stopwords and 'by' in split_title[1]:
            #     print before[-1] + ' ' + find_me + ' ' + ' '.join(after[0:4])

        except:
            pass
    print len(found)
    print number_found

    # image_set = models.Image.objects.filter(book_identifier='')
    # for image in image_set:
    #     print image.id
    #     print image
    #
    #     print '*****'
    # print len(image_set)


tests()







