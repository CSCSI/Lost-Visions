import os
from lost_visions.utils.ImagePicker import ImagePicker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import pprint
from types import NoneType
from django.db.models import Count
from lost_visions import models
# from lost_visions.utils.ImagePicker import ImagePicker

__author__ = 'lostvisions'


def get_tag_order_weight(tag_orders, tag):
    tag_weight_total = 0
    for tag_order in tag_orders:
        if len(tag_order) < 9:
            tag_order = '100100100'

        user_order = ''.join(tag_order[0:3])
        hypernym_order = ''.join(tag_order[3:6])
        synonym_order = ''.join(tag_order[6:9])

        user_order = int(user_order.lstrip('0').rstrip('0'))
        hypernym_order = int(hypernym_order.lstrip('0').rstrip('0'))
        synonym_order = int(synonym_order.lstrip('0').rstrip('0'))

        tag_weight_total += (1/float(user_order)) * (1/float(hypernym_order))

    # print tag, tag_order, user_order, hypernym_order, synonym_order, tag_weight
    return tag_weight_total


def get_similar_images_with_tags(id_alpha, im):

    tags_for_image = models.Tag.objects.all().filter(image__flickr_id=id_alpha).values('tag', 'tag_order')
            # .annotate(uses=Count('tag'))
    tags_for_image = list(tags_for_image)

    tags_for_image = sorted(tags_for_image, key=lambda image: image['tag_order'])

    print pprint.pformat(tags_for_image)

    weighted_tags_for_alpha_image = {}

    for alpha_tag in tags_for_image:
        if weighted_tags_for_alpha_image.get(alpha_tag['tag'], None) is None:
            weighted_tag = {}
            tag_orders = []

            for alpha_tag2 in tags_for_image:
                if alpha_tag2['tag'] == alpha_tag['tag']:
                    tag_orders.append(str(alpha_tag2['tag_order']))

            weighted_tag['tag_orders'] = tag_orders
            weighted_tag['weight'] = get_tag_order_weight(tag_orders, alpha_tag['tag'])
            weighted_tags_for_alpha_image[alpha_tag['tag']] = weighted_tag

    print pprint.pformat(weighted_tags_for_alpha_image)

    to_search = []
    for tag in weighted_tags_for_alpha_image.keys():
        if ' ' not in tag:
            to_search.append(tag)

    print pprint.pformat(to_search)

    # im = ImagePicker()
    res = im.get_tagged_images_for_tags_again(to_search)


    to_join = []

    discovered = []

    count = 0
    for x in res:
        count += 1

        count2 = 0
        matched2 = []
        # print x.flickr_id
        # print pprint.pformat(x.__dict__.get('flickr_id'))
        # all_image_ids += x.flickr_id + ','
        if type(x.flickr_id) is not NoneType and x.flickr_id != id_alpha and x.flickr_id not in to_join:
            to_join.append(x.flickr_id)

            # tags_for_image2 = models.Tag.objects.all().filter(image__flickr_id=x.flickr_id).values('tag') \
            # .annotate(uses=Count('tag'))
            tags_for_image2 = im.get_tags_for_image(x.flickr_id)
            # print tags_for_image2
            # tags_for_image2 = list(tags_for_image2)
            for tag2 in tags_for_image2:
                if tag2 in to_search and tag2 not in matched2:
                    count2 += 1
                    matched2.append(tag2)
            if count2 > 1:
                # print count2
                # print x.flickr_id
                # print pprint.pformat((x.flickr_id, tags_for_image2))
                # print '\n'
                discovered.append({
                    'flickr_id': x.flickr_id,
                    'matches': count2,
                    'tags': matched2
                })

    sorted_tag_matches = sorted(discovered, key=lambda image: image['matches'], reverse=True)

    print '\nFOUND MATCHES\n'
    print pprint.pformat(sorted_tag_matches)

    for tag_set in sorted_tag_matches:
        print '\n'
        print pprint.pformat(tag_set)

        weighted_tag_sum = 0

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

        weighted_tags_for_found_image = {}
        for image_tag in tags_for_found_image:
            if weighted_tags_for_found_image.get(image_tag['tag'], None) is None:
                weighted_tag = {}
                tag_orders = []

                for image_tag2 in tags_for_image:
                    if image_tag2['tag'] == image_tag['tag']:
                        tag_orders.append(str(image_tag2['tag_order']))

                weighted_tag['tag_orders'] = tag_orders
                weighted_tag['weight'] = get_tag_order_weight(tag_orders, image_tag)
                weighted_tags_for_found_image[image_tag['tag']] = weighted_tag
                weighted_tag_sum += weighted_tag['weight'] * weighted_tags_for_alpha_image[image_tag['tag']]['weight']

        for discovered_image in sorted_tag_matches:
            if discovered_image['flickr_id'] == tag_set['flickr_id']:
                discovered_image['weighted_importance'] = weighted_tag_sum
                discovered_image['weighted_tags'] = weighted_tags_for_found_image

        print pprint.pformat(weighted_tags_for_found_image)

    print '\nFOUND MATCHES\n'
    print pprint.pformat(sorted_tag_matches)

    print '\nWEIGHTED DISCOVERIES\n'
    sorted_discovered = sorted(sorted_tag_matches, key=lambda image: image['weighted_importance'], reverse=True)
    print pprint.pformat(sorted_discovered)

    finals = []
    for final_found in sorted_discovered:
        finals.append(final_found['flickr_id'])

    return finals

im = ImagePicker()
print get_similar_images_with_tags('10999645275', im)