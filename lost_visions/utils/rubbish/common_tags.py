import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import pprint
from types import NoneType
from django.db.models import Count
from lost_visions import models
from lost_visions.utils.ImagePicker import ImagePicker

__author__ = 'lostvisions'


id_alpha = '10999645275'

tags_for_image = models.Tag.objects.all().filter(image__flickr_id=id_alpha).values('tag') \
        .annotate(uses=Count('tag'))
tags_for_image = list(tags_for_image)
print pprint.pformat(tags_for_image)

to_search = []
for tag in tags_for_image:
    if ' ' not in tag['tag']:
        to_search.append(str(tag['tag']))

print pprint.pformat(to_search)

im = ImagePicker()
res = im.get_tagged_images_for_tags_again(to_search)


to_join = []
count = 0
for x in res[:500]:
    count += 1

    count2 = 0
    # print x.flickr_id
    # print pprint.pformat(x.__dict__.get('flickr_id'))
    # all_image_ids += x.flickr_id + ','
    if type(x.flickr_id) is not NoneType and x.flickr_id != id_alpha:
        to_join.append(x.flickr_id)

        tags_for_image2 = models.Tag.objects.all().filter(image__flickr_id=x.flickr_id).values('tag') \
        .annotate(uses=Count('tag'))
        tags_for_image2 = list(tags_for_image2)
        for tag2 in tags_for_image2:
            if tag2['tag'] in to_search:
                # print tag2['tag']
                count2 += 1
        if count2 > 1:
            print count2
            print x.flickr_id
            print pprint.pformat((x.flickr_id, tags_for_image2))
            print '\n'


print count
