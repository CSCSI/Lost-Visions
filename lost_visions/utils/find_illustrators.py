import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

import re
from django.db.models import Q
from lost_visions import models

__author__ = 'ubuntu'


def find(find_me, by_word):
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

                                    book_for_image = models.Book.objects.get(
                                        book_identifier=found[image].book_identifier, volume=found[image].volume)

                                    if 'author' in after_str.lower() or "l'auteur" in after_str.lower() or "himself" in after_str.lower() or "herself" in after_str.lower():
                                        print '(author) ' + found[image].first_author

                                        author_illustrator = models.BookIllustrator()
                                        author_illustrator.name = found[image].first_author
                                        author_illustrator.book = book_for_image
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

                                    illustrator = models.BookIllustrator()
                                    illustrator.name = name
                                    illustrator.book = book_for_image
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


techs = []
techs.append(['illust', 'by'])
techs.append(['illust', 'par'])
techs.append(['illust', 'de'])
techs.append(['etch', 'by'])
techs.append(['draw', 'by'])
for creation_tech in techs:
    find(creation_tech[0], creation_tech[1])