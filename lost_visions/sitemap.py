from dateutil import parser
from django.core.urlresolvers import reverse

__author__ = 'ubuntu'

from django.contrib.sitemaps import Sitemap
from lost_visions.models import Image


class ImageSitemapStub():
    def __init__(self, flickr_id):
        self.flickr_id = flickr_id
        self.location = reverse('image', kwargs={'image_id': flickr_id})

    date = ''
    changefreq = "never"
    priority = 0.5
    lastmod = parser.parse('2015-03-30')
    location = ''
    flickr_id = ''
    # image_location = 'here'


class ImageSitemap(Sitemap):

    date = ''
    changefreq = "never"
    priority = 0.5

    def __init__(self, date):
        self.date = date

    def items(self):
        image_items = []

        image_objects = Image.objects.filter(date=self.date).values_list('flickr_id', flat=True)
        for flickr_id in image_objects:
            image_items.append(ImageSitemapStub(flickr_id))

        return image_items

    def lastmod(self, obj):
        return obj.lastmod

    def location(self, obj):
        return obj.location
