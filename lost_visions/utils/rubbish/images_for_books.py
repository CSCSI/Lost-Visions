import os
import pprint
from django.core.urlresolvers import reverse
from django.db import connection
import requests
from crowdsource import settings
from crowdsource.settings import recorded_image_root, resized_start, web_server_start_resized
from lost_visions import models
from lost_visions.utils.ImageInfo import sanitise_image_info
from lost_visions.utils.db_tools import find_image, get_tested_azure_url, get_thumbnail_image

__author__ = 'ubuntu'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")


def get_book_images(book_id):
    where = ' where im.book_identifier = "003871282"'

    query = 'SELECT il."location", im."id", im."views_begun", im."views_completed", im."volume", im."publisher", im."title", im."first_author", im."BL_DLS_ID", im."pubplace", im."book_identifier", im."ARK_id_of_book", im."date", im."flickr_url", im."image_idx", im."page", im."flickr_id", im."flickr_small_source", im."flickr_small_height", im."flickr_small_width", im."flickr_medium_source", im."flickr_medium_height", im."flickr_medium_width", im."flickr_large_source", im."flickr_large_height", im."flickr_large_width", im."flickr_original_source", im."flickr_original_height", im."flickr_original_width"'' \
    from "image" as im left outer join lost_visions_imagelocation as il \
    on im.book_identifier = il.book_id and im.volume = il.volume and im.page = il.page and im.image_idx = il.idx'
    query += where

    fast_image_data = models.Image.objects.db_manager('default').raw(query, [])

    # print fast_image_data.query

    # print fast_image_data.count()

    b = []

    for a in fast_image_data:
        c = {'author': a.first_author,
             'title': a.title,
             'flickr_id': a.flickr_id,
             'location': a.location,
             'page': a.page,
             'book_id': a.book_identifier,
             'flickr_url': a.flickr_medium_source,
             'flickr_original_height': a.flickr_original_height.strip(),
             'flickr_original_width': a.flickr_original_width.strip(),
             'flickr_original': a.flickr_original_source,
             'date': a.date,
             'link': reverse('image', kwargs={'image_id': int(a.flickr_id)})
        }

    #     db_tools.get_image_info

    #     which does:

        # image_info = get_info_from_image_model(image_model)

        #       which does:

        if c['flickr_url'] == '':
            c['flickr_url'] = a.flickr_original_source

        #  then

        try:
            # actually checks to see if the image is there....
            arcca_image = find_image(c)
        except:
            arcca_image == None

        c['arcca_url'] = ''
        if arcca_image:
            c['arcca_url'] = arcca_image


    # sanitise_image_info

    # which does...

        c['image_area'] = int(c['flickr_original_height']) * int(c['flickr_original_width'])

        if c.get('arcca_url', '') == '':
            c['imageurl'] = c['flickr_url']
        else:
            c['imageurl'] = c['arcca_url']

        #  then

        if c.get('img', '') is '':
            c['img'] = a.flickr_small_source

        image_path = a.location
        if image_path is None:
            raise Exception('Location from DB is None')

        image_path = image_path.replace(recorded_image_root, resized_start) + '.thumb.jpg'

        image_web_path = image_path.replace(resized_start, web_server_start_resized)

        if os.access(image_path, os.R_OK):
            c['img_small'] = image_web_path

        if c.get('img_small', '') == '':
            c['img_small'] = a.flickr_small_source

        b.append(c)

    # print pprint.pformat(b)


    # print len(connection.queries)
    return b
