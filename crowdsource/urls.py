from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'lost_visions.views.home', name='home'),
    url(r'^image/(?P<image_id>\d+)', 'lost_visions.views.image', name='image'),
    url(r'^image/tags', 'lost_visions.views.image_tags', name='image.tags'),
    url(r'^image/random', 'lost_visions.views.random_image', name='image.random'),
    url(r'^image/grabflickr', 'lost_visions.views.grab_flickr', name='image.grab_flickr'),

    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
