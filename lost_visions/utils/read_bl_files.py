import os
from lost_visions.models import Image

__author__ = 'ubuntu'


def import_folder( folder ):

    count = 0

    for a_file in os.listdir(folder):
        
        full_path = os.path.join(folder, a_file)
        if os.path.isfile(full_path) and count < 20:
            print full_path
            count += 1

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

                        image.save()

import_folder('/home/ubuntu/flickr_files/imagedirectory')