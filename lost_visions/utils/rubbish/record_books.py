import pprint
import datetime
import pytz
from django.utils import timezone

from lost_visions import models

__author__ = 'ubuntu'


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

unique_book_images = models.Image.objects.all().values_list('book_identifier', flat=True).distinct()

print unique_book_images.count()
print unique_book_images

count = 0

for a in unique_book_images:
    # print pprint.pformat(a)

    unique_book_image_set = models.Image.objects.filter(book_identifier=a).all()[:1]
    # print unique_book_image_set.query

    unique_book_image = unique_book_image_set[0]
    # print pprint.pformat(unique_book_image.__dict__)

    date_int = 1000
    if len(unique_book_image.date):
        try:
            date_int = int(unique_book_image.date)
        except Exception as e:
            print e
            date_int = 1000


    book_model = models.Book()

    book_model.volume = unique_book_image.volume
    book_model.publisher = unique_book_image.publisher
    book_model.title = unique_book_image.title
    book_model.first_author = unique_book_image.first_author
    book_model.BL_DLS_ID = unique_book_image.BL_DLS_ID
    book_model.pubplace = unique_book_image.pubplace
    book_model.book_identifier = unique_book_image.book_identifier
    book_model.ARK_id_of_book = unique_book_image.ARK_id_of_book
    book_model.date = unique_book_image.date
    book_model.datetime = datetime.datetime(year=date_int, month=1, day=1, tzinfo=timezone.utc)

    try:
        book_model.save()
        count += 1
    except:
        pass


print str(models.Book.objects.count())
print 'added'
print str(count)