from django.db import models

# Create your models here.

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

class Image(models.Model):
    id = models.IntegerField(primary_key=True)
    identifier = models.CharField(max_length=120L)
    tags = models.CharField(max_length=256L, blank=True)
    imageurl = models.CharField(max_length=120L, blank=True)
    book = models.ForeignKey('Book', null=True, blank=True)

    class Meta:
        db_table = 'image'