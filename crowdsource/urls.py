from django.conf.urls import patterns, include, url
from django.contrib import admin
# from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect


admin.autodiscover()
# dajaxice_autodiscover()


urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', lambda r : HttpResponseRedirect('/home')),

                       url(r'^$', 'lost_visions.views.home', name='home'),
                       url(r'^about_us', 'lost_visions.views.aboutus', name='about_us'),
                       url(r'^software', 'lost_visions.views.software', name='software'),
                       url(r'^stats', 'lost_visions.views.stats', name='stats'),

                       url(r'^login', 'lost_visions.views.login', name='login'),
                       url(r'^do_login', 'lost_visions.views.do_login', name='login.do_login'),

                       url(r'^logout', 'lost_visions.views.logout', name='logout'),
                       url(r'^user_dl_all', 'lost_visions.views.user_dl_all', name='user_dl_all'),
                       url(r'^download_collection', 'lost_visions.views.download_collection', name='dl_collection'),
                       url(r'^manage_collection', 'lost_visions.views.manage_collection', name='manage_collection'),

                       url(r'^user_profile', 'lost_visions.views.user_home', name='user_profile_home'),
                       url(r'^tweet_card', 'lost_visions.views.tweet_card', name='tweet_card'),

                       url(r'^save_image', 'lost_visions.views.save_image', name='user_profile.save_image'),
                       url(r'^new_collection', 'lost_visions.views.new_collection', name='user_profile.new_collection'),

                       url(r'^signup', 'lost_visions.views.signup', name='signup'),
                       url(r'^do_signup', 'lost_visions.views.do_signup', name='signup.do_signup'),

                       url(r'^image/coords/(?P<image_id>\d+)', 'lost_visions.views.coords', name='image.coords'),
                       url(r'^image/map/(?P<image_id>\d+)', 'lost_visions.views.map', name='image.map'),

                       url(r'^image/(?P<image_id>\d+)', 'lost_visions.views.image', name='image'),

                       url(r'^search/(?P<word>[\w\+]+)', 'lost_visions.views.search', name='do_search'),
                       url(r'^search_advanced', 'lost_visions.views.search_advanced', name='search_advanced'),
                       url(r'^do_search_advanced', 'lost_visions.views.do_advanced_search', name='do_advanced_search'),
                       url(r'^get_image_data', 'lost_visions.views.get_image_data', name='get_image_data'),


                       url(r'^data_autocomplete', 'lost_visions.views.data_autocomplete', name='data.autocomplete'),


                       url(r'^image/tags', 'lost_visions.views.image_tags', name='image.tags'),
                       url(r'^image/category', 'lost_visions.views.image_category', name='image.category'),
                       url(r'^image/random', 'lost_visions.views.random_image', name='image.random'),
                       url(r'^image/grabflickr', 'lost_visions.views.grab_flickr', name='image.grab_flickr'),

                       url(r'^search_haystack/', include('haystack.urls')),

                       url(r'^oed/(?P<word>\w+)', 'lost_visions.views.oed', name='oed'),
                       url(r'^findword', 'lost_visions.views.findword', name='find.word'),

                       url(r'^find_page/(?P<book_id>\w+)/(?P<page>\w+)/(?P<volume>\w+)', 'lost_visions.views.find_page', name='find_page'),
                       url(r'^page_turner/(?P<book_id>\w+)/(?P<page>\S+)/(?P<volume>\w+)', 'lost_visions.views.page_turner', name='page_turner'),

                       # url(r'^categories', 'lost_visions.views.get_categories_html', name='categories_url'),
                       # url(r'^creation_techniques', 'lost_visions.views.get_creation_techniques_html', name='creation_techniques_url'),
                       # url(r'^free_text', 'lost_visions.views.free_text_html', name='free_text_description_url'),
                       # url(r'^new_tags', 'lost_visions.views.new_tags_html', name='new_tags_url'),
                       # url(r'^thank_you', 'lost_visions.views.thank_you_html', name='thank_you_url'),

                       # url('', include('social.apps.django_app.urls', namespace='social')),

                       # url(r'^blog/', include('blog.urls')),
                       # url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
                       # url(r'^admin_tools/', include('admin_tools.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/', include('allauth.urls'))

)

urlpatterns += staticfiles_urlpatterns()