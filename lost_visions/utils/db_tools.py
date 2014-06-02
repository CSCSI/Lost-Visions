import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import json
from django.db.models import Q
from crowdsource.settings import BASE_DIR, STATIC_URL
from random import randint
from django.core import serializers
from lost_visions import models, wordnet
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'ubuntu'


def get_next_image_id():
    image_id = None
    try:
        # min_view_count = models.Image.objects.aggregate(Min('user_count'))
        # min_viewed_image = models.Image.objects.get(user_count=min_view_count['user_count__min'])

        number_of_images = models.Image.objects.count()
        rand_image_pk = randint(1, number_of_images)
        # flickr_id=10998459416
        min_viewed_image = models.Image.objects.get(pk=rand_image_pk)
        # data = serializers.serialize("json", [min_viewed_image, ])

        # print data
        # image_id = str(min_viewed_image.identifier)
        image_id = str(min_viewed_image.flickr_id)
    except ObjectDoesNotExist as e:
        print e
        pass

    if image_id is None:
        return get_next_image_id()
    else:
        return image_id


def get_info_from_image_model(image_model):
    image_json = serializers.serialize("json", [image_model, ])
    image_object = json.loads(image_json)
    image_info = image_object[0]['fields']

    image_info['imageurl'] = image_model.flickr_medium_source
    image_info['imageurl_original'] = image_model.flickr_original_source

    if image_info['imageurl'] == '':
        image_info['imageurl'] = image_model.flickr_original_source

    return image_info


def find_image(image_info):
    try:
        # print image_info

        # web_folder = os.path.join('', 'static')
        web_folder = os.path.join('', 'media')
        web_folder = os.path.join(web_folder, 'images')
        web_folder = os.path.join(web_folder, 'scans')

        medium_folder = os.path.join(web_folder, 'medium')
        medium_folder = os.path.join(medium_folder, image_info['date'].strip())
        root_folder = os.path.join(BASE_DIR, 'lost_visions')
        root_folder = os.path.join(root_folder, 'static')
        root_folder = os.path.join(root_folder, medium_folder)

        for a_file in os.listdir(root_folder):
            try:
                # image_for_id = models.Image.objects.get(flickr_id=a_file.split('_')[0])
                # if image_for_id:
                #     print 'found' + a_file
                full_path = os.path.join(root_folder, a_file)
                filename_split = a_file.split('_')
                if os.path.isfile(full_path) and filename_split[0] == image_info['book_identifier']:
                    if filename_split[1] == image_info['volume']:
                        print '**' + full_path
                        print filename_split[2]
                        print image_info['page']
                        if filename_split[2].lstrip('0') == image_info['page'].lstrip('0'):
                            image_root_url = os.path.join(STATIC_URL, medium_folder)
                            file_url = os.path.join(image_root_url, a_file)
                            print file_url
                            return file_url
                            # return STATIC_URL + 'bl_images/' + a_file
            except Exception as e:
                print e
                pass

        scan_folder = os.path.join(web_folder, 'plates')
        scan_folder = os.path.join(scan_folder, image_info['date'].strip())
        root_folder = os.path.join(BASE_DIR, 'lost_visions')
        root_folder = os.path.join(root_folder, 'static')
        root_folder = os.path.join(root_folder, scan_folder)

        for a_file in os.listdir(root_folder):
            try:
                # image_for_id = models.Image.objects.get(flickr_id=a_file.split('_')[0])
                # if image_for_id:
                #     print 'found' + a_file
                full_path = os.path.join(root_folder, a_file)
                filename_split = a_file.split('_')
                if os.path.isfile(full_path) and filename_split[0] == image_info['book_identifier']:
                    if filename_split[1] == image_info['volume']:
                        print full_path
                        print filename_split[2]
                        print image_info['page']
                        if filename_split[2].lstrip('0') == image_info['page'].lstrip('0'):
                            image_root_url = os.path.join(STATIC_URL, scan_folder)
                            file_url = os.path.join(image_root_url, a_file)
                            print file_url
                            return file_url
                            # return STATIC_URL + 'bl_images/' + a_file
            except Exception as e:
                print e
                pass

        scan_folder = os.path.join(web_folder, 'covers')
        scan_folder = os.path.join(scan_folder, image_info['date'].strip())
        root_folder = os.path.join(BASE_DIR, 'lost_visions')
        root_folder = os.path.join(root_folder, 'static')
        root_folder = os.path.join(root_folder, scan_folder)

        for a_file in os.listdir(root_folder):
            try:
                # image_for_id = models.Image.objects.get(flickr_id=a_file.split('_')[0])
                # if image_for_id:
                #     print 'found' + a_file
                full_path = os.path.join(root_folder, a_file)
                filename_split = a_file.split('_')
                if os.path.isfile(full_path) and filename_split[0] == image_info['book_identifier']:
                    if filename_split[1] == image_info['volume']:
                        print full_path
                        print filename_split[2]
                        print image_info['page']
                        if filename_split[2].lstrip('0') == image_info['page'].lstrip('0'):
                            image_root_url = os.path.join(STATIC_URL, scan_folder)
                            file_url = os.path.join(image_root_url, a_file)
                            print file_url
                            return file_url
                            # return STATIC_URL + 'bl_images/' + a_file
            except Exception as e:
                print e
                pass
    except:
        pass
    return None


def get_image_info(image_id):
    try:
        image_for_id = models.Image.objects.get(flickr_id=image_id)
        image_info = get_info_from_image_model(image_for_id)

        arcca_image = find_image(image_info)

        if arcca_image:
            image_info['imageurl'] = arcca_image
            image_info['arcca'] = True
        else:
            image_info['arcca'] = False

        if image_info['imageurl'] == '':
            print 'ERROR with IMAGE_ID = ' + image_id
            return None
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


def save_books_from_images():
    image_set = models.Image.objects.all()

    for image in image_set:
        try:
            models.Book.objects.get(book_identifier=image.book_identifier, volume=image.volume)
            print 'Already have book ' + image.book_identifier + ' vol ' + image.volume
        except ObjectDoesNotExist:
            new_book = models.Book()
            new_book.volume = image.volume
            new_book.publisher = image.publisher
            new_book.title = image.title
            new_book.first_author = image.first_author
            new_book.BL_DLS_ID = image.BL_DLS_ID
            new_book.book_identifier = image.book_identifier
            new_book.ARK_id_of_book = image.ARK_id_of_book
            new_book.date = image.date

            print 'Saving book ' + image.book_identifier + ' vol ' + image.volume

            new_book.save()

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


            # image_set = models.Image.objects.filter(book_identifier='')
            # for image in image_set:
            #     print image.id
            #     print image
            #
            #     print '*****'
            # print len(image_set)


def tests():
    print ''


def backup_db():
    data = serializers.serialize("json", models.LostVisionUser.objects.all())
    out = open("lostvisionsuser.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.Tag.objects.all())
    out = open("tag.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.GeoTag.objects.all())
    out = open("geotag.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.ImageText.objects.all())
    out = open("imagetext.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.SavedImages.objects.all())
    out = open("savedimages.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.SearchQuery.objects.all())
    out = open("searchquery.json", "w")
    out.write(data)
    out.close()

    data = serializers.serialize("json", models.User.objects.all())
    out = open("tag.json", "w")
    out.write(data)
    out.close()


#
# SELECT lemma, definition FROM words LEFT JOIN senses s USING (wordid)
# LEFT JOIN synsets USING (synsetid) where lemma like '%churc%' order by pos limit 30
#
def search_wordnet(searchword, limit=30):
    query = "SELECT wordid, lemma, definition FROM words LEFT JOIN senses s USING (wordid) " \
            "LEFT JOIN synsets USING (synsetid) where lemma like %s " \
            "order by length(lemma) COLLATE NOCASE ASC limit %s"

    results = wordnet.Words.objects.db_manager('wordnet').raw(query, [searchword + '%', limit])
    return results


# print search_wordnet('word')

