import logging
import os
from dateutil.tz import tzlocal
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
from lost_visions import models, LostVisionUser
import csv
import datetime

__author__ = 'lostvisions'

# human_tag_file = '/media/New Volume/humantaghistory.tsv'
human_tag_file = './humantaghistory.tsv'
logger = logging.getLogger('lost_visions')


def do_log(str_to_log):
    print str_to_log
    logger.debug(datetime.datetime.now(tzlocal()).strftime('%Y-%m-%d %H:%M:%S %Z') + ' : ' + str_to_log)


def import_human_tags():

    try:
        do_log('start BL tag dump import')

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

        row_count = 0 #139190
        with open(human_tag_file, 'rb') as csvfile:

            rowreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

            flickr_user = models.User.objects.get(username='Flickr_import')
            flickr_lv_user = models.LostVisionUser.objects.get(username=flickr_user)

            for row in rowreader:
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
                    tag = models.Tag()
                    tag.tag = tag_text
                    tag.image = image_model
                    tag.user = flickr_lv_user
                    tag.timestamp = datetime.datetime.now(tzlocal())
                    tag.tag_order = 0
                    tag.save()

                    print row

                except ObjectDoesNotExist as dne:
                    pass
                except Exception as e:
                    do_log(str(type(e)) + ' : ' + str(e))
                    pass

    except Exception as e2:
        do_log(str(e2))
try:
    import_human_tags()
except Exception as e1:
    print e1

