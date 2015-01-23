import operator
import pprint
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.templatetags.static import static
import requests
from crowdsource import settings
from crowdsource.settings import recorded_image_root, resized_start, web_server_start
from lost_visions import models
from lost_visions.utils import db_tools
from lost_visions.utils.db_tools import get_tested_azure_url, get_thumbnail_image

__author__ = 'ubuntu'


def get_image_data_from_array(id_list, request):
    tag_results_dict = dict()
    trimmed_id_list = []

    # q_or_objects = []
    where = ' where (flickr_id = '
    for image_id in id_list:
        if image_id:
            # q_or_objects.append(Q(flickr_id=image_id))
            trimmed_id_list.append(image_id)

    where += ' or flickr_id = '.join(['%s' for i in range(0, len(trimmed_id_list))])

    where += ');'

    print 'getting image data from list::' + str(trimmed_id_list)
    if len(trimmed_id_list) > 0:
        # image_data = models.Image.objects.filter(reduce(operator.or_, q_or_objects))
        # print image_data.query
        # print pprint.pformat(image_data)

        query = 'SELECT il."location", im."id", im."views_begun", im."views_completed", im."volume", im."publisher", im."title", im."first_author", im."BL_DLS_ID", im."pubplace", im."book_identifier", im."ARK_id_of_book", im."date", im."flickr_url", im."image_idx", im."page", im."flickr_id", im."flickr_small_source", im."flickr_small_height", im."flickr_small_width", im."flickr_medium_source", im."flickr_medium_height", im."flickr_medium_width", im."flickr_large_source", im."flickr_large_height", im."flickr_large_width", im."flickr_original_source", im."flickr_original_height", im."flickr_original_width"'' \
        from "image" as im left outer join lost_visions_imagelocation as il \
        on im.book_identifier = il.book_id and im.volume = il.volume and im.page = il.page and im.image_idx = il.idx'
        query += where

        fast_image_data = models.Image.objects.db_manager('default').raw(query, trimmed_id_list)
        # print fast_image_data.query
        # for res in fast_image_data:
        #     print res.id
        #     print pprint.pformat(res.__dict__)
        #     print '****\n'

        for result in fast_image_data:
            try:
                tag_result = dict()
                tag_result['title'] = result.title

                try:
                    image_info = db_tools.get_image_info(result)
                    image_info = sanitise_image_info(image_info, request)

                    tag_result['img'] = image_info['imageurl']
                except Exception as e5:
                    print 'error 57382 ' + str(e5)
                    tag_result['img'] = result.flickr_small_source

                if tag_result['img'] is None:
                    tag_result['img'] = result.flickr_small_source

                if settings.use_flickr:
                    tag_result['img_small'] = result.flickr_small_source
                else:
                    try:
                        tag_result['img_small'] = get_thumbnail_image(result)
                        # tag_result['img_small'] = result.location
                    except Exception as e:
                        pass
                        # print 'error ' + str(e)

                # If we don't have a small image url yet, go find one.
                # print 'img-small : ' + tag_result.get('img_small', 'no img-small')
                if tag_result.get('img_small', '') == '':

                    try:
                        arcca_smaller_url = reverse('image.smaller_image', kwargs={
                            'book_identifier': result.book_identifier,
                            'volume': result.volume,
                            'page': result.page,
                            'image_idx': result.image_idx
                        })
                        checking_url = request.build_absolute_uri(arcca_smaller_url)
                        r = requests.head(checking_url, stream=True)
                        # print checking_url, r
                        if r.status_code is requests.codes.ok:
                            tag_result['img_small'] = arcca_smaller_url
                        else:
                            raise
                    except Exception as e2:
                        print 'error 1355#' + str(e2)
                        tag_result['img_small'] = result.flickr_small_source

                tag_result['date'] = result.date
                tag_result['page'] = result.page.lstrip('0')
                tag_result['book_id'] = result.book_identifier
                tag_result['author'] = result.first_author
                tag_result['link'] = reverse('image', kwargs={'image_id': int(result.flickr_id)})

                tag_results_dict[result.flickr_id] = tag_result
            except Exception as e88:
                print 'error 3455##' + str(e88)
                pass
    return tag_results_dict



# I am very sorry for whoever finds this....
# Basically all URLs cannot be trusted, so we brute force
# Prefer ARCCA, then azure, then flickr.
def sanitise_image_info(image_info, request):
    image_info['image_area'] = int(image_info['flickr_original_height']) * int(image_info['flickr_original_width'])

    image_info['azure'] = get_tested_azure_url(image_info)

    r = requests.head(request.build_absolute_uri(static(image_info['arcca_url'])), stream=True, timeout=0.3)
    if r.status_code is not requests.codes.ok:
        if image_info['azure']:
            image_info['imageurl'] = image_info['azure']
        else:
            image_info['imageurl'] = image_info['flickr_url']
    else:
        image_info['imageurl'] = image_info['arcca_url']
    return image_info