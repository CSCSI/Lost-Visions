from dateutil import parser
from django.core.urlresolvers import reverse

__author__ = 'ubuntu'

from django.contrib.sitemaps import Sitemap
from lost_visions.models import Image


class ImageSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Image.objects.all()[:500]

    def lastmod(self, obj):
        return parser.parse('2015-03-30')

    def location(self, obj):
        return reverse('image', kwargs={'image_id': obj.flickr_id})