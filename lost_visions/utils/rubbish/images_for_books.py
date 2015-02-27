import os
import pprint
from django.db import connection
from lost_visions import models
from lost_visions.utils.ImageInfo import sanitise_image_info
from lost_visions.utils.db_tools import find_image

__author__ = 'ubuntu'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")


where = ' where im.book_identifier = "003871282"'

query = 'SELECT il."location", im."id", im."views_begun", im."views_completed", im."volume", im."publisher", im."title", im."first_author", im."BL_DLS_ID", im."pubplace", im."book_identifier", im."ARK_id_of_book", im."date", im."flickr_url", im."image_idx", im."page", im."flickr_id", im."flickr_small_source", im."flickr_small_height", im."flickr_small_width", im."flickr_medium_source", im."flickr_medium_height", im."flickr_medium_width", im."flickr_large_source", im."flickr_large_height", im."flickr_large_width", im."flickr_original_source", im."flickr_original_height", im."flickr_original_width"'' \
from "image" as im left outer join lost_visions_imagelocation as il \
on im.book_identifier = il.book_id and im.volume = il.volume and im.page = il.page and im.image_idx = il.idx'
query += where

fast_image_data = models.Image.objects.db_manager('default').raw(query, [])

print fast_image_data.query

# print fast_image_data.count()

b = []

for a in fast_image_data:
    c = {
        'author': a.first_author,
        'flickr_id': a.flickr_id,
        'location': a.location,
        'page': a.page,
        'book_identifier': a.book_identifier,
        'flickr_url': a.flickr_url,
        'flickr_original_height': a.flickr_original_height.strip(),
        'flickr_original_width': a.flickr_original_width.strip()
    }

    d = find_image(c)

    c = sanitise_image_info(c, None)

    c['d'] = d

    b.append(c)

    print pprint.pformat(c)


# print len(connection.queries)

# print pprint.pformat(b)

print len(connection.queries)
