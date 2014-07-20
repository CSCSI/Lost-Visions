from lost_visions import models

__author__ = 'ubuntu'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")


def analyse_tags():


    query = 'select distinct tag, id, count(tag) as count from lost_visions_tag' \
            ' as count group by tag order by count desc;'
    tag_counts = models.Tag.objects.raw(query, [])

    print tag_counts.query

    for tag_with_count in tag_counts:
        if tag_with_count.tag != 'Bone' and tag_with_count.tag != 'Flint':
            print '\n\nworking with : ' + tag_with_count.tag + ':' + str(tag_with_count.count)
            image_ids_with_tag = models.Tag.objects.filter(tag=tag_with_count.tag).values('image__flickr_id').distinct()

            # print 'images with this tag :' + str(image_ids_with_tag)

            repeat_tags = dict()
            for image_id in image_ids_with_tag:
                # print 'image ' + str(image_id['image__flickr_id']) + ' has tag ' + tag_with_count.tag
                image = models.Tag.objects.filter(image__flickr_id=image_id['image__flickr_id'])

                for image_tags in image:
                    if repeat_tags.has_key(image_tags.tag):
                        repeat_tags[image_tags.tag] = (repeat_tags[image_tags.tag] + 1)
                    else:
                        repeat_tags[image_tags.tag] = 1

            for w in list(sorted(repeat_tags, key=repeat_tags.get, reverse=True))[:3]:
                print w, repeat_tags[w]

analyse_tags()