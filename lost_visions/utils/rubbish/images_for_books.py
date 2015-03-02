import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
from crowdsource.settings import recorded_image_root, resized_start, web_server_start_resized, bl_image_root
from lost_visions import models
from lost_visions.utils.db_tools import find_image

__author__ = 'ubuntu'


def get_book_images(book_id):

    # print type(book_id), book_id

    query = 'SELECT il."location", im."id", im."views_begun", im."views_completed", ' \
            'im."volume", im."publisher", im."title", im."first_author", im."BL_DLS_ID", ' \
            'im."pubplace", im."book_identifier", im."ARK_id_of_book", im."date", im."flickr_url", ' \
            'im."image_idx", im."page", im."flickr_id", im."flickr_small_source", ' \
            'im."flickr_small_height", im."flickr_small_width", im."flickr_medium_source", ' \
            'im."flickr_medium_height", im."flickr_medium_width", im."flickr_large_source", ' \
            'im."flickr_large_height", im."flickr_large_width", im."flickr_original_source", ' \
            'im."flickr_original_height", im."flickr_original_width" ' \
            'from "image" as im left outer join lost_visions_imagelocation as il ' \
            'on im.book_identifier = il.book_id and im.volume = il.volume and ' \
            'im.page = il.page and im.image_idx = il.idx where im.book_identifier = %s'

    fast_image_data = models.Image.objects.db_manager('default').raw(query, [str(book_id)])

    # print fast_image_data.query

    return get_image_data_for_array(fast_image_data)

def get_image_data_for_array(image_data):

    b = []

    for a in image_data:
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
             # 'link': reverse('image', kwargs={'image_id': int(a.flickr_id)})
        }

        #     db_tools.get_image_info

        #     which does:

        # image_info = get_info_from_image_model(image_model)

        #       which does:

        if c['flickr_url'] == '':
            c['flickr_url'] = a.flickr_original_source

            #  then

            # try:
            # actually checks to see if the image is there....

        arcca_image = find_image(c)

        c['arcca_url'] = ''
        not_found = False

        if arcca_image:
            c['arcca_url'] = arcca_image

            image_path = a.location
            image_path = image_path.replace(recorded_image_root, bl_image_root)

            if os.access(image_path, os.R_OK):
                c['imageurl'] = c['arcca_url']

                small_image_path = image_path.replace(recorded_image_root, resized_start) + '.thumb.jpg'
                if os.access(small_image_path, os.R_OK):

                    small_image_web_path = small_image_path.replace(resized_start, web_server_start_resized)
                    c['img_small'] = small_image_web_path

            else:
                not_found = True
        else:
            not_found = True

        if not_found:
            c['imageurl'] = c['flickr_url']
            c['img'] = a.flickr_original_source
            c['img_small'] = a.flickr_small_source

        c['image_area'] = int(c['flickr_original_height']) * int(c['flickr_original_width'])

        b.append(c)

    return b

# k = '003871282'
#
# print pprint.pformat(get_book_images(k))


def weighted_tags_low_db():
    tag_set = {
        'flickr_id': '345678',
        'tags': ['dog', 'cat']
    }

    tags_for_found_image = []

    for image_tag in tag_set['tags']:
        tag = models.Tag.objects.filter(image__flickr_id=tag_set['flickr_id']).filter(tag=image_tag)
        for tag_orders in tag:
            print image_tag
            print tag_orders.tag_order
            tags_for_found_image.append({
                'tag': image_tag,
                'tag_order': tag_orders.tag_order
            })