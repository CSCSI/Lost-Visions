__author__ = 'ubuntu'

import datetime
from haystack import indexes
from lost_visions.models import Image


class ImageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # author = indexes.CharField(model_attr='user')
    # pub_date = indexes.DateTimeField(model_attr='pub_date')

    volume = indexes.CharField(model_attr='volume')
    publisher = indexes.CharField(model_attr='publisher')
    title = indexes.CharField(model_attr='title')
    first_author = indexes.CharField(model_attr='first_author')
    BL_DLS_ID = indexes.CharField(model_attr='BL_DLS_ID')
    pubplace = indexes.CharField(model_attr='pubplace')
    book_identifier = indexes.CharField(model_attr='book_identifier')
    ARK_id_of_book = indexes.CharField(model_attr='ARK_id_of_book')
    date = indexes.CharField(model_attr='date')
    flickr_url = indexes.CharField(model_attr='flickr_url')
    image_idx = indexes.CharField(model_attr='image_idx')
    page = indexes.CharField(model_attr='page')
    flickr_id = indexes.CharField(model_attr='flickr_id')

    flickr_small_source = indexes.CharField(model_attr='flickr_small_source')
    flickr_small_height = indexes.CharField(model_attr='flickr_small_height')
    flickr_small_width = indexes.CharField(model_attr='flickr_small_width')
    flickr_medium_source = indexes.CharField(model_attr='flickr_medium_source')
    flickr_medium_height = indexes.CharField(model_attr='flickr_medium_height')
    flickr_medium_width = indexes.CharField(model_attr='flickr_medium_width')
    flickr_large_source = indexes.CharField(model_attr='flickr_large_source')
    flickr_large_height = indexes.CharField(model_attr='flickr_large_height')
    flickr_large_width = indexes.CharField(model_attr='flickr_large_width')
    flickr_original_source = indexes.CharField(model_attr='flickr_original_source')
    flickr_original_height = indexes.CharField(model_attr='flickr_original_height')
    flickr_original_width = indexes.CharField(model_attr='flickr_original_width')

    def get_model(self):
        return Image



