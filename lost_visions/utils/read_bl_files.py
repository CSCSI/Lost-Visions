import os
from time import sleep
import urllib
from django.db.utils import IntegrityError
from crowdsource import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
from lost_visions.models import Image

__author__ = 'ubuntu'


def ss(row):
    return row.strip("\n").split("\t")


def find_small(folder, output_folder):
    print output_folder
    count = 0

    for a_file in os.listdir(folder):

        full_path = os.path.join(folder, a_file)
        fileName, fileExtension = os.path.splitext(full_path)
        date = a_file.split('_')[0]
        date_path = os.path.join(os.path.join(settings.BASE_DIR, 'bl_images'), date)
        print date_path

        if os.path.exists(date_path):

            if os.path.isfile(full_path) and 'small' in fileName and fileExtension == '.tsv': #and count < 20:
                print full_path

                with open(full_path, "r") as metadata_src:
                    headers = ss(metadata_src.readline())
                    for line in metadata_src:
                        metadata = dict(zip(headers, ss(line)))

                        # print date_path
                        download_output_path = os.path.join(date_path, bl_filename(metadata))

                        # date_path = settings.BASE_DIR + '/bl_images/' + date

                        # download_output_path = date_path + '/' + bl_filename(metadata)

                        url_to_azure = azure_url(metadata)



                        try:
                            os.stat(date_path)
                        except:
                            os.mkdir(date_path)
                            pass

                        if not os.path.exists(download_output_path):
                            print url_to_azure
                            print download_output_path
                            try:
                                urllib.urlretrieve (url_to_azure, download_output_path)
                            except Exception as e:
                                print e

                                pass
                    # try:
                    #     os.stat(download_output_path)
                    #     else:
                    #         print download_output_path + ' already exists'
                        # except:
                        #
                        #     pass

        else:
            print 'folder ' + date_path + ' exists.'


def azure_url(metadata):
    return u"http://blmc.blob.core.windows.net/{0[date]}/{0[book_identifier]}_{0[volume]}_{0[page]}_{0[image_idx]}_{0[date]}_embellishments.jpg".format(metadata)


def bl_filename(metadata):
    return u"" \
           u"{0[book_identifier]}_{0[volume]}_{0[page]}_{0[image_idx]}_{0[date]}_embellishments.jpg".format(metadata)

def import_folder( folder , database='default'):

    count = 0

    for a_file in os.listdir(folder):

        full_path = os.path.join(folder, a_file)
        fileName, fileExtension = os.path.splitext(full_path)

        if os.path.isfile(full_path) and fileExtension == '.tsv': #and count < 20:
            print full_path
            count += 1

            already_saved = 0
            with open(full_path) as f:
                for i, line in enumerate(f):
                    if i > 0:

                        image = Image()
                        words = line.split('\t')

                        if len(words) > 24:

                            image.volume = words[0]
                            image.publisher = words[1]
                            image.title = words[2]
                            image.first_author = words[3]
                            image.BL_DLS_ID = words[4]
                            image.pubplace = words[5]
                            image.book_identifier = words[6]
                            image.ARK_id_of_book = words[7]
                            image.date = words[8]
                            image.flickr_url = words[9]
                            image.image_idx = words[10]
                            image.page = words[11]
                            image.flickr_id = words[12]
                            image.flickr_small_source = words[13]
                            image.flickr_small_height = words[14]
                            image.flickr_small_width = words[15]
                            image.flickr_medium_source = words[16]
                            image.flickr_medium_height = words[17]
                            image.flickr_medium_width = words[18]
                            image.flickr_large_source = words[19]
                            image.flickr_large_height = words[20]
                            image.flickr_large_width = words[21]
                            image.flickr_original_source = words[22]
                            image.flickr_original_height = words[23]
                            image.flickr_original_width = words[24]

                            try:
                                image.save(using=database)
                            except IntegrityError as i:
                                already_saved += 1
                                print 'Already saved image : ' + image.flickr_id

                            if already_saved > 10:
                                break

import_folder(settings.bl_folder, 'postgres')

# find_small(settings.bl_folder, os.path.join(settings.BASE_DIR, 'bl_images'))
