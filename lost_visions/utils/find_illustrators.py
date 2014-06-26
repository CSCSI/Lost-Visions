import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import re
from django.db.models import Q
from lost_visions import models

__author__ = 'ubuntu'


def find(find_me, by_word, save=False):
    image_set = models.Image.objects.filter(Q(title__contains=find_me))

    found = dict()
    number_found = 0
    for image in image_set:
        found[image.book_identifier] = image

    for image in found:
        try:
            title = found[image].title
            title_split = title.split()
            for index, word in enumerate(title_split):
                if find_me.lower() in word.lower():
                    before = title_split[0:index]
                    after = title_split[index+1:]
                    after_str = ' '.join(after)
                    if by_word in after_str:
                        for index2, word2 in enumerate(after):
                            if by_word.lower() == word2.lower():
                                previous_word = after[index2 -1].lower()
                                if 'edited' not in previous_word and 'introduction' not in previous_word and 'verses' not in previous_word:

                                    # book_for_image = models.Book.objects.get(
                                    #     book_identifier=found[image].book_identifier, volume=found[image].volume)

                                    if 'author' in after_str.lower() or "l'auteur" in after_str.lower() or "himself" in after_str.lower() or "herself" in after_str.lower():
                                        print '(author) ' + found[image].first_author

                                        if save:
                                            author_illustrator = models.BookIllustrator()
                                            author_illustrator.name = found[image].first_author
                                            # author_illustrator.book = book_for_image
                                            author_illustrator.technique = find_me
                                            author_illustrator.save()

                                    name_uncleaned = ' '.join(after[index2+1:])

                                    name = re.sub('[\[\]\(\)]', '', name_uncleaned)
                                    name = re.sub('[^ (\S{1,3}\.*\s)*(\S*.)]', '', name)

                                    name = trim_name(name).strip()
                                    name = name.replace('...', '').rstrip('.').rstrip(',').strip()

                                    print name
                                    print found[image].title
                                    print found[image].flickr_id
                                    print '\n'

                                    if save:
                                        illustrator = models.BookIllustrator()
                                        illustrator.name = name
                                        # illustrator.book = book_for_image
                                        illustrator.technique = find_me
                                        illustrator.save()

                                    number_found += 1
        except:
            pass
    print len(found)
    print number_found


def trim_name(name):
    name_split = name.split()
    name_rebuilt = ''
    for name_part in name_split:
        name_rebuilt += name_part
        if (name_part[-1] == '.' or name_part[-1] == ';') and len(name_part) > 4:
            return name_rebuilt
        else:
            name_rebuilt += ' '
    return name_rebuilt


def old_illustrator_search():
    techs = []
    techs.append(['illust', 'by'])
    techs.append(['illust', 'par'])
    techs.append(['illust', 'de'])
    techs.append(['etch', 'by'])
    techs.append(['draw', 'by'])
    for creation_tech in techs:
        find(creation_tech[0], creation_tech[1])


def find_illustrators(save=True):
    image_set = models.Image.objects.filter()\
        .values_list('title', 'book_identifier', 'volume', 'first_author').distinct()

    number_found = 0

    for image in image_set.iterator():
        techs = []

        techs.append(['illust', 'by'])
        techs.append(['etch', 'by'])
        techs.append(['draw', 'by'])
        techs.append(['plate', 'by'])

        techs.append(['design', 'by'])
        techs.append(['photo', 'by'])
        techs.append(['litho', 'by'])
        techs.append(['mezzo', 'by'])

        techs.append(['sculp', 'by'])
        techs.append(['pinct', 'by'])
        techs.append(['draw', 'by'])


        # techs.append(['bild', 'von'])
        techs.append(['tafel', 'von'])
        techs.append(['gravur', 'von'])
        techs.append(['skizze', 'von'])

        techs.append(['schnitt', 'von'])
        techs.append(['stich', 'von'])
        techs.append(['atzung', 'von'])
        techs.append(['lithograph', 'von'])

        techs.append(['illust', 'par'])
        techs.append(['dessin', 'par'])
        techs.append(['esquiss', 'par'])
        techs.append(['planch', 'par'])
        techs.append(['gravur', 'par'])
        techs.append(['manier', 'par'])

        for creation_tech in techs:
            find_me = creation_tech[0]
            by_word = creation_tech[1]

            try:
                title = image[0]
                book_id = image[1]
                volume = image[2]
                author = image[3]

                title_split = title.split()
                for index, word in enumerate(title_split):
                    if find_me.lower() in word.lower():
                        before = title_split[0:index]
                        after = title_split[index+1:]
                        after_str = ' '.join(after)
                        if by_word in after_str:
                            for index2, word2 in enumerate(after):
                                if by_word.lower() == word2.lower():
                                    previous_word = after[index2 -1].lower()
                                    if 'edited' not in previous_word and 'introduction' not in previous_word and 'verses' not in previous_word:

                                        # book_for_image = models.Book.objects.get(
                                        #     book_identifier=book_id, volume=volume)

                                        if 'author' in after_str.lower() or "l'auteur" in after_str.lower() or "himself" in after_str.lower() or "herself" in after_str.lower():
                                            print '(author) ' + author

                                            if save:
                                                author_illustrator = models.BookIllustrator()
                                                author_illustrator.name = author
                                                author_illustrator.book_id = book_id
                                                author_illustrator.technique = find_me
                                                author_illustrator.save()

                                        name_uncleaned = ' '.join(after[index2+1:])

                                        name = re.sub('[\[\]\(\)]', '', name_uncleaned)
                                        name = re.sub('[^ (\S{1,3}\.*\s)*(\S*.)]', '', name)

                                        name = trim_name(name).strip()
                                        name = name.replace('...', '').rstrip('.').rstrip(',').strip()

                                        print find_me
                                        print name
                                        print title
                                        print book_id
                                        print '\n'

                                        if save:
                                            illustrator = models.BookIllustrator()
                                            illustrator.name = name
                                            illustrator.book_id = book_id
                                            illustrator.technique = find_me
                                            illustrator.save()

                                        number_found += 1
            except Exception as e:
                print e
                pass
    print number_found


def find_distinct():
    image_set = models.Image.objects.filter().values_list('title', 'book_identifier').distinct()
    print image_set.query
    print image_set


def db_test():
    # illustrator = 'author'
    # found = models.BookIllustrator.objects\
    #             .filter(name__icontains=illustrator).values_list('book_id', flat=True).distinct()

    image_set = models.Image.objects.filter()\
        .values_list('title', 'book_identifier', 'volume', 'first_author').distinct()

    for a in image_set:
        print a

db_test()

# find_illustrators(save=True)
# find_distinct()