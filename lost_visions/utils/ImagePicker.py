import logging
import os
from haystack.backends import SQ
from haystack.inputs import Raw
from haystack.query import SearchQuerySet

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
import pprint
from crowdsource.settings import db_regex_char
from lost_visions.utils import db_tools


from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
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

        keywords = request.GET.get('keyword', '')
        keywords = keywords.split(' ')

        year = request.GET.get('year', '')
        author = request.GET.get('author', '')
        illustrator = request.GET.get('illustrator', '')
        number_of_results = request.GET.get('num_results', '')
        book_id = request.GET.get('book_id', '')
        publisher = request.GET.get('publisher', '')
        publishing_place = request.GET.get('publishing_place', '')
        title = request.GET.get('title', '')

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

        if len(illustrator):
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

        all_results = all_results.values_list('flickr_id', flat=True).distinct()[:5000]
        logger.debug(all_results.query)
        return all_results

    def advanced_haystack_search(self, query_items, similar_tags=False):

        regex_string = r"{0}"

        print query_items

        keywords = query_items.get('keyword', '')
        keywords = keywords.split(' ')

        year = query_items.get('year', '')
        author = query_items.get('author', '')
        illustrator = query_items.get('illustrator', '')
        number_of_results = query_items.get('num_results', '')
        book_id = query_items.get('book_id', '')
        publisher = query_items.get('publisher', '')
        publishing_place = query_items.get('publishing_place', '')
        title = query_items.get('title', '')

        tag_keywords_only = query_items.get('tag_keywords_only', False)

        all_results = SearchQuerySet()

        if len(year):
            decade = year[0:3]
            all_results = all_results.filter((SQ(date__startswith=decade)))

        if len(author):
            all_results = all_results.filter(SQ(first_author=Raw(author + '*')))

        if len(title):
            all_results = all_results.filter(SQ(title=Raw(title + '*')))

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
            all_results = all_results.filter(SQ(publisher=Raw(publisher + '*')))
            filtered = True

        if len(publishing_place):
            all_results = all_results.filter(SQ(pubplace=Raw(publishing_place + '*')))
            filtered = True

        if similar_tags:
            similar_words = []
            for word in keywords:
                similar_words.extend(self.get_similar_word_array(word))
            keywords = similar_words

        for word in keywords:
            if len(word):
                regex_format = regex_string.format(word)
                ors = [
                    SQ(tag=Raw(regex_format + '*')),
                    SQ(caption=Raw(regex_format + '*')),
                    SQ(description=Raw(regex_format + '*')),
                    ]

                if not tag_keywords_only:
                    ors += [
                        SQ(first_author=Raw(regex_format + '*')),
                        SQ(date__contains=regex_format),
                        # SQ(title__contains=regex_format),
                        SQ(title=Raw(regex_format + '*')),

                        SQ(publisher=Raw(regex_format + '*')),
                        SQ(pubplace=Raw(regex_format + '*')),

                        ]

                all_results = all_results.filter(reduce(operator.or_, ors))

        # all_results_list = all_results.values_list('fields__flickr_id', flat=True)

        logger.debug(all_results.query)
        print all_results.query
        return all_results


class Request():
    def __init__(self):
        self.GET = {
            # 'author': 'BETTANY',
            'keyword': 'tree water'
        }



# image_picker = ImagePicker()
#
# # for j in range(0, 1):
# #     print image_picker.get_untagged_image(1)
# #
# #     print image_picker.get_untagged_images(3)
# #
# #     print '\n'
#
#
# number_queries = len(connection.queries)
#
# # print image_picker.get_tagged_images_for_tags(['man', 'woman'], and_or='or')
#
# # print image_picker.get_tagged_images_for_similar_tag('boy')
#
# adv_res = image_picker.advanced_search(request=Request())
#
# pprint_object(adv_res)
#
# print ('\n\nbefore {} after {} diff {}'.format(number_queries,
#                                                len(connection.queries),
#                                                str(len(connection.queries) - number_queries)))
# qus = len(connection.queries) - number_queries
# # print connection.queries[:(qus * -1)]
#
# # pprint_object(connection.queries)
