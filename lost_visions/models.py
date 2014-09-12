import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
# import watson
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class LostVisionUser(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    username = models.ForeignKey(User, blank=False)
    expert_level = models.IntegerField(default=0, blank=True)
    self_description = models.CharField(max_length=256L, blank=True)
    sign_up_timestamp = models.DateTimeField(auto_now=False, blank=True, null=True)
    last_login = models.DateTimeField(auto_now=False, blank=True, null=True)
    number_logins = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return str(self.id) + ':' + self.username.username


class Book(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    volume = models.CharField(max_length=120L, blank=True)
    publisher = models.CharField(max_length=256L, blank=True)
    title = models.CharField(max_length=256L)
    first_author = models.CharField(max_length=120L, blank=True)
    BL_DLS_ID = models.CharField(max_length=120L, blank=True)
    pubplace = models.CharField(max_length=120L, blank=True)
    book_identifier = models.CharField(max_length=120L, blank=True)
    ARK_id_of_book = models.CharField(max_length=120L, blank=True)
    date = models.CharField(max_length=120L, blank=True)
    # author = models.ForeignKey('Person', null=True, blank=True, related_name='author')
    # illustrator = models.ForeignKey('Person', null=True, blank=True, related_name='illustrator')

    class Meta:
        db_table = 'book'


class ImageLocation(models.Model):
    location = models.TextField(blank=True)
    image = models.ForeignKey('Image', null=True, blank=True, related_name='image')


class Image(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    # a count of number of times image is presented to user
    # includes both search results and full image request
    #
    views_begun = models.IntegerField(default=0, blank=True)

    # a count of number of times users have returned tagging info
    views_completed = models.IntegerField(default=0, blank=True)

    # identifier = models.CharField(max_length=120L)
    # tags = models.CharField(max_length=256L, blank=True)
    # imageurl = models.CharField(max_length=120L, blank=True)
    # user_count = models.IntegerField(default=0)
    # book = models.ForeignKey('Book', null=True, blank=True)
    # tags1 = models.ManyToManyField(UserImageTags)

    volume = models.CharField(max_length=256L, blank=True)
    publisher = models.CharField(max_length=256L, blank=True)
    # title = models.CharField(max_length=256L, blank=True)
    title = models.TextField(blank=True)

    first_author = models.CharField(max_length=256L, blank=True)
    BL_DLS_ID = models.CharField(max_length=256L, blank=True)
    pubplace = models.CharField(max_length=256L, blank=True)
    book_identifier = models.CharField(max_length=256L, blank=True)
    ARK_id_of_book = models.CharField(max_length=256L, blank=True)
    date = models.CharField(max_length=256L, blank=True)
    flickr_url = models.CharField(max_length=256L, blank=True)
    image_idx = models.CharField(max_length=256L, blank=True)
    page = models.CharField(max_length=256L, blank=True)
    flickr_id = models.CharField(max_length=256L, blank=False, unique=True)
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
        return str(self.id) + ':' + self.flickr_id


class Tag(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    tag = models.CharField(max_length=256L, blank=False)
    user = models.ForeignKey(LostVisionUser, blank=False)
    image = models.ForeignKey(Image, blank=False)
    x_percent = models.CharField(max_length=256L, blank=True)
    y_percent = models.CharField(max_length=256L, blank=True)
    timestamp = models.DateTimeField(auto_now=False, blank=True)
    tag_order = models.IntegerField(blank=True)

    def __unicode__(self):
        user = self.user.username.username
        image = self.image.flickr_id

        return str(self.id) + ':' + self.tag + ':' + user + ':' + image


class GeoTag(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    user = models.ForeignKey(LostVisionUser, blank=False)
    image = models.ForeignKey(Image, blank=False)
    north_east_x = models.CharField(max_length=256L, blank=True)
    north_east_y = models.CharField(max_length=256L, blank=True)
    south_west_x = models.CharField(max_length=256L, blank=True)
    south_west_y = models.CharField(max_length=256L, blank=True)

    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)
    tag_order = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        user = self.user.username.username
        image = self.image.flickr_id

        return str(self.id) + ':' + user + ':' + image + ':[' + self.north_east_x + ':' \
               + self.north_east_y + ']:[' + self.south_west_x + ':' + self.south_west_y + ']'


class SearchQuery(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    search_term = models.CharField(max_length=256L, blank=False)
    timestamp = models.DateTimeField(auto_now=True, blank=True)
    user = models.ForeignKey(LostVisionUser, blank=True)

    def __unicode__(self):
        user = self.user.username.username

        return str(self.id) + ':' + user + ':' + self.search_term + ':' \
               + self.timestamp.strftime('%Y-%m-%d %H:%M:%S')


class ImageText(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    caption = models.TextField()
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)
    user = models.ForeignKey(LostVisionUser, blank=True)
    image = models.ForeignKey(Image, blank=False)

    def __unicode__(self):
        username = ''
        if self.user:
            username = self.user.username.username
        ts = ''
        if self.timestamp:
            ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        return str(self.id) + ':' + username + ':' + self.caption + ':' + ts


class SavedImages(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    user = models.ForeignKey(LostVisionUser, blank=True)
    image = models.ForeignKey(Image, blank=False)
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __unicode__(self):
        user = self.user.username.username

        return str(self.id) + ':' + user + ':' \
               + self.image.flickr_id + ':' + self.timestamp.strftime('%Y-%m-%d %H:%M:%S')


class BookIllustrator(models.Model):
    # id = models.IntegerField(primary_key=True)
    # id = models.AutoField(primary_key=True)

    book_id = models.CharField(max_length=120L, blank=False)
    name = models.CharField(max_length=120L, blank=True)
    technique = models.CharField(max_length=120L, blank=True)

    class Meta:
        unique_together = ('book_id', 'name', 'technique')

    def __unicode__(self):

        return str(self.id) + ':' + str(self.book_id) + ':' + self.name + ':' + str(self.technique)


class LinkedImage(models.Model):
    image = models.ForeignKey(Image, blank=False)
    name = models.CharField(max_length=120L, blank=True)
    file_name = models.CharField(max_length=120L, blank=True)
    location = models.CharField(max_length=120L, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return str(self.id) + ':' + self.image.flickr_id + ':' + self.name


class ImageCollection(models.Model):
    name = models.CharField(max_length=120L, blank=True)
    user = models.ForeignKey(LostVisionUser, blank=False)
    public = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __unicode__(self):
        return str(self.id) + ':' + str(self.user.username.username) + ':' + self.name + ':' + str(self.public)


class ImageMapping(models.Model):
    image = models.ForeignKey(Image, blank=False)
    collection = models.ForeignKey(ImageCollection, blank=False)
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __unicode__(self):
        return str(self.id) + ':' + str(self.image.flickr_id) \
               + ':' + self.collection.name + ':' + self.collection.user.username.username




# watson.register(Image)
# watson.register(ImageText)
