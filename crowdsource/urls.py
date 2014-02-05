from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'lost_visions.views.home', name='home'),
    url(r'^image/(?P<image_id>\d+)', 'lost_visions.views.image', name='image'),
    url(r'^image/tags', 'lost_visions.views.image_tags', name='image.tags'),

    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
