from itertools import islice
import logging
import os
import pprint
from bleach import clean
from dateutil.tz import tzlocal, parser
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from lost_visions.utils import db_tools

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
from lost_visions import models, LostVisionUser
import csv
import datetime

import nltk
from nltk.corpus import wordnet as wn

__author__ = 'lostvisions'

human_tag_file = '/media/New Volume/humantaghistory.tsv'
# human_tag_file = './humantaghistory.tsv'
# human_tag_file = '/media/New Volume/local_tags.tsv'

logger = logging.getLogger('lost_visions')


def do_log(str_to_log):
    print str_to_log
    logger.debug(datetime.datetime.now(tzlocal()).strftime('%Y-%m-%d %H:%M:%S %Z') + ' : ' + str_to_log)


def catch_edge_cases(tag_text):
    if tag_text.lower() == 'portrait':
        return [{'desc': 'any likeness of a person, in any medium',
                  'label': u'portrait',
                  'sensenum': 2,
                  'synset': u'portrait.n.2'}]
    return None


def alt_tags(tag_text, image, user):
    tag_synset = None

    if len(tag_text) == 1:
        return

    synsets = catch_edge_cases(tag_text)

    if synsets is None:
        stem = wn.morphy(tag_text.lower())
        if stem is not None:
            tag_text = stem

        synsets = db_tools.wordnet_formatted(tag_text)

        print tag_text
        for synset in synsets:
            if synset['label'] == tag_text.lower() and synset['sensenum'] == 1 and '.n.' in synset['synset']:
                print pprint.pformat(synset)
                tag_synset = synset['synset']

    else:
        if len(synsets) > 0:
            tag_synset = synsets[0]['synset']

    if tag_synset is not None:

        alternative_words = db_tools.list_wordnet_links(tag_synset)[::-1]

        for index, weighted_word in enumerate(alternative_words):
            word = weighted_word[0]
            print word

            tag_order = str((int(clean(str(0), strip=True)) + 1) * 100)

            tag_hyp_dist = int(weighted_word[1][0]) + 1
            tag_syn_val = int(weighted_word[1][1]) + 1
            tag_order += str(tag_hyp_dist * 100) + str(tag_syn_val * 100)

            write_tag(word, image, user, tag_order=tag_order)


def write_tag(tag_text, image_model, flickr_lv_user, tag_order='0'):
    tag = models.Tag()
    tag.tag = tag_text
    tag.image = image_model
    tag.user = flickr_lv_user
    tag.timestamp = datetime.datetime.now(tzlocal())
    tag.tag_order = tag_order
    # tag.save()

    # print tag.__dict__


def get_flickr_user():
    try:
        test_flickr_user = models.User.objects.get(username='Flickr_import')
    except:

        time_now = timezone.now()
        new_user = models.User()
        new_user.username = 'Flickr_import'
        new_user.first_name = 'flickr'
        new_user.email = 'fake@email.com'
        new_user.set_password('flickr')
        new_user.save()

        lv_user = LostVisionUser(username=new_user, sign_up_timestamp=time_now)
        lv_user.save()

    flickr_user = models.User.objects.get(username='Flickr_import')
    flickr_lv_user = models.LostVisionUser.objects.get(username=flickr_user)

    return flickr_lv_user


def import_human_tags():

    try:
        do_log('start BL tag dump import')

        flickr_lv_user = get_flickr_user()

        row_count = 0 #139190
        with open(human_tag_file, 'rb') as csvfile:

            rowreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

            for row in islice(rowreader, 3000, None):
                row_count += 1

                if row_count%100 == 0:
                    percent_complete = (float(row_count) / 139190) * 100
                    two_d_p_str = str(float("{0:.2f}".format(percent_complete))) + '%'
                    print two_d_p_str
                    do_log(two_d_p_str)

                image_id = row[0]
                tag_text = row[1]
                try:
                    image_model = models.Image.objects.get(flickr_id=image_id)

                    print '\n'
                    print tag_text

                    write_tag(tag_text, image_model, flickr_lv_user)

                    alt_tags(tag_text, image_model, flickr_lv_user)

                    print row

                except ObjectDoesNotExist as dne:
                    pass
                except Exception as e:
                    do_log(str(type(e)) + ' : ' + str(e))

    except Exception as e2:
        do_log(str(e2))


# def tag_image():
#     user_tag = 'portrait'
#     image_id = '10997096956'
#     flickr_user = get_flickr_user()
#     image_model = models.Image.objects.get(flickr_id=image_id)
#
#     alt_tags(user_tag, image_model, flickr_user)

# tag_image()

try:
    import_human_tags()
except Exception as e1:
    print e1



# print pprint.pformat(db_tools.wordnet_formatted('portrait'))