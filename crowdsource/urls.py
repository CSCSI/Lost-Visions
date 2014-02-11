from django.conf.urls import patterns, include, url
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

admin.autodiscover()
dajaxice_autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'lost_visions.views.home', name='home'),
    url(r'^image/(?P<image_id>\d+)', 'lost_visions.views.image', name='image'),
    url(r'^image/tags', 'lost_visions.views.image_tags', name='image.tags'),
    url(r'^image/random', 'lost_visions.views.random_image', name='image.random'),
    url(r'^image/grabflickr', 'lost_visions.views.grab_flickr', name='image.grab_flickr'),

    url(r'^categories', 'lost_visions.views.get_categories_html', name='categories_url'),
    url(r'^creation_techniques', 'lost_visions.views.get_creation_techniques_html', name='creation_techniques_url'),
    url(r'^free_text', 'lost_visions.views.free_text_html', name='free_text_description_url'),


    # url(r'^blog/', include('blog.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
