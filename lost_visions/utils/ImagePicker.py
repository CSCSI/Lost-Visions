import logging
import os
import string
from types import NoneType
from haystack.backends import SQ
from haystack.inputs import Raw
from haystack.query import SearchQuerySet
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
import pprint
from crowdsource.settings import db_regex_char
from lost_visions.utils import db_tools
from django.core.exceptions import ObjectDoesNotExist
import operator
from django.db.models import Q
from random import randint
from django.core import serializers
from lost_visions import models

logger = logging.getLogger('lost_visions')

__author__ = 'ubuntu'


class ImagePicker():
    def __init__(self):
        # saves continually calculating this
        self.image_db_size = models.Image.objects.count()
        # print('db size {}'.format(self.image_db_size))

    # can cause multiple db accesses on django models
    def pprint_object(self, obj):
        print pprint.pformat(obj, indent=1, width=80, depth=None)

    def get_untagged_image(self, retries=0, allowed_retries=100):
        rand_image_pk = randint(1, self.image_db_size)

        # number_queries = len(connection.queries)
        try:
            an_image = models.Image.objects.get(pk=rand_image_pk)
        except ObjectDoesNotExist:
            retries += 1
            return self.get_untagged_image(retries)

        image_tag_count = models.Tag.objects.filter(image=an_image).count()

        if image_tag_count == 0 and an_image.flickr_id != '':
            # print ('before {} after {} diff {}'.format(number_queries,
            #                                            len(connection.queries),
            #                                            str(len(connection.queries) - number_queries)))
            return str(an_image.flickr_id)

        else:
            print('moving on...')

            if an_image.flickr_id == '':
                print serializers.serialize('json', [an_image, ]) + '\n'

            retries += 1
            print('retries {}'.format(retries))
            if retries > allowed_retries:
                return None

            return self.get_untagged_image(retries=retries)

    def get_untagged_images(self, number):

        image_ids = []
        for i in range(0, int(number)):
            image_ids.append(self.get_untagged_image())
        return image_ids

    def get_tagged_images(self):
        tagged_images = models.Tag.objects.order_by().values_list('image__flickr_id', flat=True).distinct()
        return tagged_images

    def get_tagged_images_for_tag(self, tag, number=None):
        tagged_images = models.Tag.objects.filter(tag__iexact=tag).order_by().values_list('image__flickr_id', flat=True).distinct()
        return tagged_images

    def get_tags_for_image(self, flickr_id):
        all_results = SearchQuerySet()
        all_results = all_results.filter(SQ(flickr_id=flickr_id))

        tags = []
        tag_with_order = []
        for res in all_results:
            # print flickr_id
            # print pprint.pformat(res.__dict__)
            # print type(res)
            # print res.tag
            if res.tag is not None:
                tags.append(res.tag)
                tag_with_order.append([res.tag, res.tag_order])
        return tags, tag_with_order

    def get_tagged_images_for_tags_again(self, tag_array, and_or='or', number=None):

        regex_string = r"{0}"

        # Using haystack for speed
        all_results = SearchQuerySet()
        ors = []

        for tag in tag_array:
            if len(tag.strip()):
                regex_format = regex_string.format(tag)

                ors.append(SQ(tag=Raw(regex_format + '*')))

        if len(ors) > 0:
            all_results = all_results.filter(reduce(operator.or_, ors))
        else:
            raise Exception('No tags to filter images for')

        # print all_results.query
        return list(set(all_results))

    def get_tagged_images_for_tags(self, tag_array, and_or='or', number=None):

        # only interested in images where all tags are present
        if and_or is 'and':

            # For each tag find the Tag DB objects with that tag
            tagged_images = dict()
            for tag in tag_array:
                tagged_images[tag] = (self.get_tagged_images_for_tag(tag))

            # pprint_object(tagged_images)

            # find largest list.
            # If the tag isn't in this, there's no reason looking in the others
            largest_list = []
            most_used_tag = ''
            for key_tag in tagged_images:
                if len(tagged_images[key_tag]) > len(largest_list):
                    largest_list = tagged_images[key_tag]
                    most_used_tag = key_tag

            # traverse the longest list, compare with others
            images_with_all_tags = []
            for image_in_largest_list in largest_list:
                tags_lists_image_appears_in = 0
                for key_tag in tagged_images:
                    # If the inspected list B is not the longest list A (pointless comparing A and A)
                    # and the image we're looking at from A is also in list B
                    if key_tag is not most_used_tag and image_in_largest_list in tagged_images[key_tag]:
                        # Increment the number of times we've seen it
                        tags_lists_image_appears_in += 1

                # If we say the image N-1 times, it was in every list
                # N-1 as we didn't search the longest list
                if tags_lists_image_appears_in == len(tag_array) - 1:
                    # Add image to return list
                    images_with_all_tags.append(image_in_largest_list)

            if number is not None:
                images_with_all_tags = images_with_all_tags[:number]

            return images_with_all_tags

        # assume 'or', so any one of the given tags gives a hit
        else:
            # 'reduce' the input list to a long list of "OR"s and filter for all
            tagged_images = models.Tag.objects.filter(reduce(operator.or_, (Q(tag__iexact=x) for x in tag_array))).order_by().values_list('image__flickr_id', flat=True).distinct()

        return list(set(tagged_images))

    def search_keyword(self, keyword):
        keywords = keyword.split(' ')

        ors = []
        for word in keywords:
            ors.append(Q(first_author__iregex=r"\b{0}\b".format(word)))
            ors.append(Q(date__iregex=r"\b{0}\b".format(word)))
            ors.append(Q(title__iregex=r"\b{0}\b".format(word)))
            ors.append(Q(publisher__iregex=r"\b{0}\b".format(word)))
            ors.append(Q(pubplace__iregex=r"\b{0}\b".format(word)))

        found = models.Image.objects.filter(reduce(operator.or_, ors)).values_list('book_identifier', flat=True).distinct()

        found = list(found)

        ors_tag = []
        for word in keywords:
            ors_tag.append(Q(tag__iregex=r"\b{0}\b".format(word)))

        tag_ids = models.Tag.objects.filter(reduce(operator.or_, ors_tag)) \
            .values_list('image__flickr_id', flat=True).distinct()

        found.extend(tag_ids)

        ors_usr_txt = []
        for word in keywords:

            ors_usr_txt.append(Q(caption__iregex=r"\b{0}\b".format(word)))
            ors_usr_txt.append(Q(description__iregex=r"\b{0}\b".format(word)))

        usr_txt_ids = models.ImageText.objects.filter(reduce(operator.or_, ors_usr_txt)) \
            .values_list('image__flickr_id', flat=True).distinct()

        found.extend(usr_txt_ids)

        return found

    def get_tagged_images_for_similar_tag(self, tag):
        # formatted_word = db_tools.wordnet_formatted(tag)
        #
        # # pprint_object(formatted_word)
        #
        # alternative_words = db_tools.list_wordnet_links(formatted_word[1]['synset'])
        #
        # # pprint_object(alternative_words)
        #
        # word_list = []
        # for word in alternative_words:
        #     word_list.append(word[0])
        #
        # pprint_object(word_list)

        word_list = self.get_similar_word_array(tag)

        find_tags = self.get_tagged_images_for_tags(word_list, and_or='or')
        return find_tags

    def get_similar_word_array(self, tag):
        formatted_word = db_tools.wordnet_formatted(tag)

        # pprint_object(formatted_word)

        alternative_words = db_tools.list_wordnet_links(formatted_word[1]['synset'])

        # pprint_object(alternative_words)

        word_list = []
        for word in alternative_words:
            word_list.append(word[0])

        self.pprint_object(word_list)

        return word_list

    def get_image_from_untagged_cluster(self):
        pass

    def predict_tags_for_image_by_cluster(self):
        pass

    def advanced_search(self, request, similar_tags=False):

        # regex_string = r"\b{0}\b"

        # db_regex_char = "\y"
        regex_string = r"\b{0}\b".replace("\\b", db_regex_char)

        print request.GET

        keywords = request.GET.get('keyword', '').strip()
        keywords = [x.strip() for x in keywords.split(' ')]

        year = request.GET.get('year', '').strip()
        author = request.GET.get('author', '').strip()
        illustrator = request.GET.get('illustrator', '').strip()
        number_of_results = request.GET.get('num_results', '').strip()
        book_id = request.GET.get('book_id', '').strip()
        publisher = request.GET.get('publisher', '').strip()
        publishing_place = request.GET.get('publishing_place', '').strip()
        title = request.GET.get('title', '').strip()

        tag_keywords_only = request.GET.get('tag_keywords_only', False)

        all_results = models.Image.objects.all()

        if len(year):
            decade = year[0:3]
            all_results = all_results.filter((Q(date__startswith=decade)))
            # filtered = True
            # readable_query += ' for the ' + year + "'s"

        if len(author):
            all_results = all_results.filter(Q(first_author__iregex=regex_string.format(author)))
            # filtered = True
            # readable_query += ' with author ' + author

        if len(title):
            all_results = all_results.filter(Q(title__iregex=regex_string.format(title)))
            # filtered = True
            # readable_query += ' with title ' + title

        if len(illustrator.strip()):
            q_or_objects = []
            for illustrator_book_id in models.BookIllustrator.objects \
                    .filter(name__iregex=regex_string.format(illustrator)).values_list('book_id', flat=True).distinct():
                if illustrator_book_id:
                    q_or_objects.append(Q(book_identifier=str(illustrator_book_id)))

            if len(q_or_objects) > 0:
                all_results = all_results.filter(reduce(operator.or_, q_or_objects))

                # filtered = True
                # readable_query += ' with illustrator ' + illustrator

        if len(book_id):
            all_results = all_results.filter(book_identifier=book_id)
            # filtered = True
            # title = models.Image.objects.values_list('title', flat=True).filter(book_identifier=book_id)[:1].get()
            # readable_query += ' for book title ' + title

        if len(publisher):
            all_results = all_results.filter(Q(publisher__iregex=regex_string.format(publisher)))
            filtered = True
            # readable_query += ' from publisher ' + publisher

        if len(publishing_place):
            all_results = all_results.filter(Q(pubplace__iregex=regex_string.format(publishing_place)))
            filtered = True
            # readable_query += ' published in ' + publishing_place

        if similar_tags:
            similar_words = []
            for word in keywords:
                if len(word):
                    similar_words.extend(self.get_similar_word_array(word))
            keywords = similar_words

        print '*' + str(keywords) + '*'
        for word in keywords:
            if len(word):
                # all_results = self.filter_all_on_tag(all_results, word)

                regex_format = regex_string.format(word)
                ors = [
                    Q(tag__tag__iregex=regex_format),
                    Q(imagetext__caption__iregex=regex_format),
                    Q(imagetext__description__iregex=regex_format),
                    ]

                if not tag_keywords_only:
                    ors += [
                        Q(first_author__iregex=regex_format),
                        Q(date__iregex=regex_format),
                        Q(title__iregex=regex_format),
                        Q(publisher__iregex=regex_format),
                        Q(pubplace__iregex=regex_format),

                        ]

                all_results = all_results.filter(reduce(operator.or_, ors))

        all_results = all_results.values_list('flickr_id', flat=True).distinct()[:500]
        logger.debug(all_results.query)
        return all_results

    def advanced_haystack_search(self, query_items, similar_tags=False):

        regex_string = r"{0}"

        print query_items

        keywords = query_items.get('keyword', '').strip()
        keywords = [x.strip() for x in keywords.split(' ')]

        year = query_items.get('year', '').strip()
        author = query_items.get('author', '').strip()
        illustrator = query_items.get('illustrator', '').strip()
        number_of_results = query_items.get('num_results', '').strip()
        book_id = query_items.get('book_id', '').strip()
        publisher = query_items.get('publisher', '').strip()
        publishing_place = query_items.get('publishing_place', '').strip()
        title = query_items.get('title', '').strip()

        tag_keywords_only = query_items.get('tag_keywords_only', False)

        all_results = SearchQuerySet()

        if len(year):
            decade = year[0:3]
            all_results = all_results.filter((SQ(date__startswith=decade)))

        if len(author):
            # all_results = all_results.filter_or(first_author__icontains='*' + author + '*')
            author_words = [x.strip() for x in author.split(' ')]
            for author_word in author_words:
                re.sub(r'\W+', '', author_word)
                all_results = all_results.filter(first_author__icontains='*' + author_word + '*')

        if len(title):
            # all_results = all_results.filter_or(title__icontains='*"' + title + '"*')
            title_words = [x.strip() for x in title.split(' ')]
            for title_word in title_words:
                re.sub(r'\W+', '', title_word)
                all_results = all_results.filter(title__icontains='*' + title_word + '*')
            # all_results = all_results.filter(SQ(title=Raw('*' + title + '*')))

        if len(illustrator):
            q_or_objects = []
            for illustrator_book_id in models.BookIllustrator.objects \
                    .filter(name__contains=regex_string.format(illustrator)).values_list('book_id', flat=True).distinct():
                if illustrator_book_id:
                    q_or_objects.append(SQ(book_identifier=str(illustrator_book_id)))

            if len(q_or_objects) > 0:
                all_results = all_results.filter(reduce(operator.or_, q_or_objects))

        if len(book_id):
            all_results = all_results.filter(book_identifier=book_id)

        if len(publisher):
            publisher_words = [x.strip() for x in publisher.split(' ')]
            for publisher_word in publisher_words:
                re.sub(r'\W+', '', publisher_word)
                all_results = all_results.filter(publisher__icontains='*' + publisher_word + '*')
            # all_results = all_results.filter(SQ(publisher=Raw('*' + publisher + '*')))

        if len(publishing_place):
            publishing_place_words = [x.strip() for x in publishing_place.split(' ')]
            for publishing_place_word in publishing_place_words:
                re.sub(r'\W+', '', publishing_place_word)
                all_results = all_results.filter(pubplace__icontains='*' + publishing_place_word + '*')
            # all_results = all_results.filter(SQ(pubplace=Raw('*' + publishing_place + '*')))

        if similar_tags:
            similar_words = []
            for word in keywords:
                if len(word):
                    similar_words.extend(self.get_similar_word_array(word))
            keywords = similar_words

        for word in keywords:
            # if len(word):
            #     regex_format = regex_string.format(word)
            #     ors = [
            #         SQ(tag=Raw('*' + regex_format + '*')),
            #         SQ(caption=Raw('*' + regex_format + '*')),
            #         SQ(description=Raw('*' + regex_format + '*')),
            #         ]
            #
            #     if not tag_keywords_only:
            #         ors += [
            #             SQ(first_author=Raw('*' + regex_format + '*')),
            #             SQ(date__contains=regex_format),
            #             # SQ(title__contains=regex_format),
            #             SQ(title=Raw('*' + regex_format + '*')),
            #
            #             SQ(publisher=Raw('*' + regex_format + '*')),
            #             SQ(pubplace=Raw('*' + regex_format + '*')),
            #
            #             ]
            #
            #     all_results = all_results.filter(reduce(operator.or_, ors))

            if len(word):
                regex_format = regex_string.format(word)

                all_results = all_results.filter_or(tag__icontains=word)
                all_results = all_results.filter_or(caption__icontains=word)
                all_results = all_results.filter_or(description__icontains=word)

                if not tag_keywords_only:
                    all_results = all_results.filter_or(first_author__icontains=word)
                    all_results = all_results.filter_or(date__icontains=word)
                    all_results = all_results.filter_or(title__icontains=word)
                    all_results = all_results.filter_or(publisher__icontains=word)
                    all_results = all_results.filter_or(pubplace__icontains=word)

        # all_results_list = all_results.values_list('fields__flickr_id', flat=True)

        logger.debug(all_results.query)
        print all_results.query
        return all_results

    # A method to find the overall tag weight for a tag
    # taking into account the tag order, for multiple taggers
    def get_tag_order_weight(self, tag_orders, tag):
        tag_weight_total = 0

        # For each tag order in the list, add up the total weight for this tag
        for tag_order in tag_orders:
            if len(tag_order) < 9:
                # print tag_order + ' becomes 100100100'
                # Some tags have the old system of 0, 1, 2, 3...
                # assume they are equally important "first order" tags
                tag_order = '100100100'

            user_order = ''.join(tag_order[0:3])
            hypernym_order = ''.join(tag_order[3:6])
            synonym_order = ''.join(tag_order[6:9])

            user_order = int(user_order.lstrip('0').rstrip('0'))
            hypernym_order = int(hypernym_order.lstrip('0').rstrip('0'))
            # For future reference, synonyms are currently considered equal
            synonym_order = int(synonym_order.lstrip('0').rstrip('0'))

            # multiply 1/ user order by 1/ hypernym order
            # eg 100100100, 200200200, 300300300 =
            # ( 1/1 * 1/1 ) + ( 1/2 * 1/2 ) + ( 1/3 * 1/3 )
            # 1 + 1/4 + 1/9 = 49/36 = 1.361
            tag_weight_total += (1/float(user_order)) * (1/float(hypernym_order))

        # print tag, tag_order, user_order, hypernym_order, synonym_order, tag_weight
        return tag_weight_total

    # A giant method to find all the images similar to "Image Alpha" based on it's tags
    def get_similar_images_with_tags(self, id_alpha):

        # Get alpha images tags and their tag order
        # Multiple users may use same tag with different tagging order
        tags_for_image = models.Tag.objects.all().filter(image__flickr_id=id_alpha).values('tag', 'tag_order')
        tags_for_image = list(tags_for_image)

        # Sort them by tagging order, for visuals only
        # ie 100100100 < 200300400 < 300400200
        tags_for_image = sorted(tags_for_image, key=lambda image: image['tag_order'])

        # print 'alpha tags : ' + pprint.pformat(tags_for_image)

        weighted_tags_for_alpha_image = {}

        # For each tag in the alpha set, look through the set and grab all tag orders
        for alpha_tag in tags_for_image:
            # Don't search for blank tags
            if len(alpha_tag['tag']):
                # Only record if we haven't already seen this tag
                if weighted_tags_for_alpha_image.get(alpha_tag['tag'], None) is None:
                    weighted_tag = {}
                    tag_orders = []

                    # We have an unseen tag from the alpha image
                    # check through all tags and see if it appears again
                    # append all tag orders to a list
                    for alpha_tag2 in tags_for_image:
                        if alpha_tag2['tag'] == alpha_tag['tag']:
                            tag_orders.append(str(alpha_tag2['tag_order']))

                    # For alpha tag we record a list of tag orders
                    # and the "weight" of this tag overall
                    weighted_tag['tag_orders'] = tag_orders
                    weighted_tag['weight'] = self.get_tag_order_weight(tag_orders, alpha_tag['tag'])
                    weighted_tags_for_alpha_image[alpha_tag['tag']] = weighted_tag

        # print 'weighted alpha tags : ' + pprint.pformat(weighted_tags_for_alpha_image)

        to_search = []

        # removing tags with spaces, as it breaks search for some reason
        # TODO figure this out
        for tag in weighted_tags_for_alpha_image.keys():
            if ' ' not in tag:
                to_search.append(tag)

        # print pprint.pformat(to_search)

        # im = ImagePicker()
        images_with_tag = []
        try:
            # Get images which have any of the tags found in the alpha image
            images_with_tag = self.get_tagged_images_for_tags_again(to_search)
        except:
            pass

        to_join = []

        discovered = []

        count = 0

        for x in images_with_tag:
            count += 1
            count2 = 0
            matched2 = []
            all_tags_for_image = []
            matched2_with_order = []

            # Haystack can be weird,
            # so we need to check this item has a flickr_id, isn't the alpha image, and isn't a repeat
            if type(x.flickr_id) is not NoneType and x.flickr_id != id_alpha and x.flickr_id not in to_join:
                to_join.append(x.flickr_id)

                # Get all the tags for this image
                tags_for_image2, tags_with_order = self.get_tags_for_image(x.flickr_id)

                # print 'tags_with_order : ' + str(tags_with_order)
                # Count the number of tags which are matched between this image and the alpha image
                for tag2 in tags_for_image2:
                    all_tags_for_image.append(tag2)
                    if tag2 in to_search and tag2 not in matched2:
                        count2 += 1
                        matched2.append(tag2)

                #         Try and store the tag_orders at the same time
                for tag2 in tags_with_order:
                    if tag2[0] in to_search and tag2[0] not in matched2_with_order:
                        count2 += 1
                        matched2_with_order.append({
                            'tag': tag2[0],
                            'tag_order': tag2[1]
                        })

                #         This could be tweaked to ensure at least 2-3 matching tags
                if count2 > 0:

                    # Record the number of matches and the list of shared tags
                    discovered.append({
                        'flickr_id': x.flickr_id,
                        'matches': count2,
                        'tags': matched2,
                        'all_tags': all_tags_for_image,
                        'all_tags_with_order': matched2_with_order
                    })

        # Sort by the number of matches
        # Assuming that number of matching tags is most relevent here, to cut down on processing
        sorted_tag_matches = sorted(discovered, key=lambda image: image['matches'], reverse=True)[:15]

        # print '\nFOUND MATCHES\n'
        # print pprint.pformat(sorted_tag_matches)

        # Now we need the weighted sums for all these matching-images tag-orders
        for tag_set in sorted_tag_matches:
            # print '\n'
            # print pprint.pformat(tag_set)

            weighted_tag_sum = 0




            # tags_for_found_image = []
            #
            # for image_tag in tag_set['tags']:
            #     # Get all the tags from the image, with tag orders
            #     # TODO do this in the DB hit above?
            #     tag = models.Tag.objects.filter(image__flickr_id=tag_set['flickr_id']).filter(tag=image_tag)
            #     for tag_orders in tag:
            #         # print image_tag
            #         # print tag_orders.tag_order
            #         tags_for_found_image.append({
            #             'tag': image_tag,
            #             'tag_order': tag_orders.tag_order
            #         })





            # Organise the weights of the tags
            weighted_tags_for_found_image = {}

            # TODO does this make things better?
            # for image_tag in tags_for_found_image:
            for image_tag in tag_set['all_tags_with_order']:

                if weighted_tags_for_found_image.get(image_tag['tag'], None) is None:
                    weighted_tag = {}
                    tag_orders = []

                    # As above with the Alpha image, get the weight for the tag
                    for image_tag2 in tags_for_image:
                        if image_tag2['tag'] == image_tag['tag']:
                            tag_orders.append(str(image_tag2['tag_order']))

                    weighted_tag['tag_orders'] = tag_orders
                    weighted_tag['weight'] = self.get_tag_order_weight(tag_orders, image_tag)
                    weighted_tags_for_found_image[image_tag['tag']] = weighted_tag

                    # This is special
                    # Multiply the weighted sum of the tag for this image
                    # by the weight for the tag in the alpha image
                    # Add the result of this to the weights for all tags for this image
                    weighted_tag_sum += weighted_tag['weight'] * weighted_tags_for_alpha_image[image_tag['tag']]['weight']

            # Add these tags and weights to the discovered image dict
            for discovered_image in sorted_tag_matches:
                if discovered_image['flickr_id'] == tag_set['flickr_id']:
                    discovered_image['weighted_importance'] = weighted_tag_sum
                    discovered_image['weighted_tags'] = weighted_tags_for_found_image

                    # print pprint.pformat(weighted_tags_for_found_image)

        # print '\nFOUND MATCHES\n'
        # print pprint.pformat(sorted_tag_matches)

        # Sort by overall calculated weight
        # print '\nWEIGHTED DISCOVERIES\n'
        sorted_discovered = sorted(sorted_tag_matches, key=lambda image: image['weighted_importance'], reverse=True)
        # print pprint.pformat(sorted_discovered)

        # Bin all that info and just return a list of flickr_IDs
        # Shame, this is probably decent stuff.
        finals = []
        for final_found in sorted_discovered:
            finals.append(final_found['flickr_id'])
            # print final_found['flickr_id'], final_found['weighted_importance']

        return finals


class Request():
    def __init__(self):
        self.GET = {
            # 'author': 'BETTANY',
            'keyword': 'tree water'
        }
