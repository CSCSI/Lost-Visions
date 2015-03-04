import datetime
from haystack import indexes
from lost_visions.models import Image, Tag, ImageText

__author__ = 'ubuntu'


class ImageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_author = indexes.CharField(model_attr='first_author')
    pubplace = indexes.CharField(model_attr='pubplace')
    title = indexes.CharField(model_attr='title')
    publisher = indexes.CharField(model_attr='publisher')
    date = indexes.CharField(model_attr='date')

    flickr_id = indexes.CharField(model_attr='flickr_id')

    def get_model(self):
        return Image

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        # return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())
        return self.get_model().objects


class TagIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    tag = indexes.CharField(model_attr='tag')
    tag_order = indexes.CharField(model_attr='tag_order')
    flickr_id = indexes.CharField(model_attr='image__flickr_id')

    def get_model(self):
        return Tag

    def get_updated_field(self):
        return "timestamp"

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())


class TextIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    caption = indexes.CharField(model_attr='caption')
    description = indexes.CharField(model_attr='description')
    flickr_id = indexes.CharField(model_attr='image__flickr_id')

    def get_model(self):
        return ImageText

    def get_updated_field(self):
        return "timestamp"

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())