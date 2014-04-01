import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class LostVisionUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.ForeignKey(User)
    expert_level = models.IntegerField(default=0, blank=True)
    self_description = models.CharField(max_length=256L, blank=True)

class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256L)
    identifier = models.CharField(max_length=120L, blank=True)
    publisher = models.CharField(max_length=256L, blank=True)
    shelfmark = models.CharField(max_length=256L, blank=True)
    author = models.ForeignKey('Person', null=True, blank=True, related_name='author')
    illustrator = models.ForeignKey('Person', null=True, blank=True, related_name='illustrator')

    class Meta:
        db_table = 'book'


class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256L)

    class Meta:
        db_table = 'person'


class Tags(models.Model):
    id = models.IntegerField(primary_key=True)
    tag = models.CharField(max_length=256L, blank=False)


class UserImageTags(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.ForeignKey(LostVisionUser)
    tags = models.ManyToManyField(Tags)

    class Meta:
        unique_together = ("id", "uid")


class Image(models.Model):
    id = models.IntegerField(primary_key=True)
    # identifier = models.CharField(max_length=120L)
    # tags = models.CharField(max_length=256L, blank=True)
    # imageurl = models.CharField(max_length=120L, blank=True)
    # user_count = models.IntegerField(default=0)
    # book = models.ForeignKey('Book', null=True, blank=True)
    tags1 = models.ManyToManyField(UserImageTags)

    volume = models.CharField(max_length=256L, blank=True)
    publisher = models.CharField(max_length=256L, blank=True)
    title = models.CharField(max_length=256L, blank=True)
    first_author = models.CharField(max_length=256L, blank=True)
    BL_DLS_ID = models.CharField(max_length=256L, blank=True)
    pubplace = models.CharField(max_length=256L, blank=True)
    book_identifier = models.CharField(max_length=256L, blank=True)
    ARK_id_of_book = models.CharField(max_length=256L, blank=True)
    date = models.CharField(max_length=256L, blank=True)
    flickr_url = models.CharField(max_length=256L, blank=True)
    image_idx = models.CharField(max_length=256L, blank=True)
    page = models.CharField(max_length=256L, blank=True)
    flickr_id = models.CharField(max_length=256L, blank=True)
    flickr_small_source = models.CharField(max_length=256L, blank=True)
    flickr_small_height = models.CharField(max_length=256L, blank=True)
    flickr_small_width = models.CharField(max_length=256L, blank=True)
    flickr_medium_source = models.CharField(max_length=256L, blank=True)
    flickr_medium_height = models.CharField(max_length=256L, blank=True)
    flickr_medium_width = models.CharField(max_length=256L, blank=True)
    flickr_large_source = models.CharField(max_length=256L, blank=True)
    flickr_large_height = models.CharField(max_length=256L, blank=True)
    flickr_large_width = models.CharField(max_length=256L, blank=True)
    flickr_original_source = models.CharField(max_length=256L, blank=True)
    flickr_original_height = models.CharField(max_length=256L, blank=True)
    flickr_original_width = models.CharField(max_length=256L, blank=True)

    class Meta:
        db_table = 'image'

    def __unicode__(self):
        return self.flickr_id

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    term = models.CharField(max_length=256L, blank=False)


class UserInterests(models.Model):
    id = models.IntegerField(primary_key=True)
    categories = models.ManyToManyField(Category)


class ExpertLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=256L, blank=True)







class ImageCategories(models.Model):
    id = models.IntegerField(primary_key=True)
