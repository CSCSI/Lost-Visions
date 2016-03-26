import pprint
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps.views import index, sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from lost_visions import models
from lost_visions.sitemap import ImageSitemap
from reimagine.views import reimagine_home

admin.autodiscover()

dates = models.Book.objects.values_list('date', flat=True).distinct()
sitemaps = {}

for date in dates:
    if not len(date):
        date = 'unknown'
    sitemaps[str(date)] = ImageSitemap(str(date))

# print pprint.pformat(sitemaps, indent=4)

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', lambda r : HttpResponseRedirect('/home')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/', include('allauth.urls')),

                       url(r'^reimagine/entry_upload', 'reimagine.views.entry_upload', name='entry_upload'),
                       url(r'^reimagine/store_competition_entry',
                           'reimagine.views.competition_entry_store',
                           name='competition_entry_store'),
                       url(r'^reimagine_rules', 'reimagine.views.reimagine_rules', name='reimagine_rules'),

                       url(r'^reimagine', 'reimagine.views.reimagine_home', name='reimagine'),

                       url(r'^sitemap\.xml$', index, {'sitemaps': sitemaps}),
                       url(r'^sitemap-(?P<section>.+)\.xml$', sitemap,
                           {'sitemaps': sitemaps, 'template_name': 'image_sitemap.html'}),

                       url(r'^$', 'lost_visions.views.home', name='home'),
                       url(r'^about_us', 'lost_visions.views.aboutus', name='about_us'),
                       url(r'^research', 'lost_visions.views.research', name='research'),
                       url(r'^software', 'lost_visions.views.software', name='software'),
                       url(r'^education', 'lost_visions.views.education', name='education'),
                       url(r'^stats', 'lost_visions.views.stats', name='stats'),
                       url(r'^help', 'lost_visions.views.help', name='help'),

                       url(r'^mario/(?P<flickr_id>\d+)', 'lost_visions.views.mario_find', name='mario'),

                       url(r'^login', 'lost_visions.views.login', name='login'),
                       url(r'^do_login', 'lost_visions.views.do_login', name='login.do_login'),

                       url(r'^logout', 'lost_visions.views.logout', name='logout'),
                       url(r'^request_public_exhibition', 'lost_visions.views.request_public_exhibition', name='request_public_exhibition'),
                       url(r'^user_dl_all', 'lost_visions.views.user_dl_all', name='user_dl_all'),
                       url(r'^download_collection', 'lost_visions.views.download_collection', name='dl_collection'),
                       url(r'^download_ready', 'lost_visions.views.download_collection_ready', name='dl_collection_ready'),
                       url(r'^zip_available/(?P<collection_id>\d+)', 'lost_visions.views.zip_available', name='zip_available'),


                       url(r'^manage_collection', 'lost_visions.views.manage_collection', name='manage_collection'),
                       url(r'^view_collection/(?P<collection_id>\d+)/(?P<page>\d+)',
                           'lost_visions.views.view_collection', name='view_collection'),

                       url(r'^user_profile', 'lost_visions.views.user_home', name='user_profile_home'),
                       url(r'^exhibition/(?P<collection_id>\d+)', 'lost_visions.views.exhibition', name='exhibition'),
                       url(r'^accept_public_exhibition/(?P<collection_id>\d+)',
                           'lost_visions.views.accept_public_exhibition', name='accept_public_exhibition'),
                                              url(r'^tweet_card', 'lost_visions.views.tweet_card', name='tweet_card'),
                       url(r'^latest_exhibition',
                           'lost_visions.views.latest_public_exhibition', name='public_exhibition'),
                       url(r'^previous_exhibition/(?P<exhibition_id>\d+)',
                           'lost_visions.views.public_exhibition_specific', name='public_exhibition_specific'),

                       url(r'^list_exhibitions', 'lost_visions.views.public_exhibition_list', name='public_exhibition_list'),
                       url(r'^tweet_card', 'lost_visions.views.tweet_card', name='tweet_card'),

                       url(r'^save_image', 'lost_visions.views.save_image', name='user_profile.save_image'),
                       url(r'^new_collection', 'lost_visions.views.new_collection', name='user_profile.new_collection'),
                       url(r'^get_api_key', 'lost_visions.views.get_api_key', name='user_profile.get_api_key'),
                       url(r'^is_api_key_valid', 'lost_visions.views.is_valid_api_key', name='user_profile.valid_api_key'),

                       url(r'^signup', 'lost_visions.views.signup', name='signup'),
                       url(r'^do_signup', 'lost_visions.views.do_signup', name='signup.do_signup'),

                       url(r'^random', 'lost_visions.views.random_search', name='random'),

                       url(r'^image/coords/(?P<image_id>\d+)', 'lost_visions.views.coords', name='image.coords'),
                       url(r'^image/coords_save', 'lost_visions.views.coords_save', name='image.coords_save'),

                       url(r'^image/map/(?P<image_id>\d+)', 'lost_visions.views.map', name='image.map'),

                       url(r'^image/(?P<image_id>\d+)', 'lost_visions.views.image', name='image'),
                       url(r'^image_data/(?P<image_id>\d+)', 'lost_visions.views.image_data', name='image_data'),
                       url(r'^similar_images/(?P<image_id>\d+)',
                           'lost_visions.views.similar_images', name='image.similar_images'),
                       url(r'^smaller_image/(?P<book_identifier>\d+)/(?P<volume>\d+)/(?P<page>\d+)/(?P<image_idx>\d+)',
                           'lost_visions.views.get_resized_image', name='image.smaller_image'),


                       url(r'^search/(?P<word>[\w\+]+)', 'lost_visions.views.search', name='do_search'),
                       url(r'^search_advanced', 'lost_visions.views.search_advanced', name='search_advanced'),
                       url(r'^do_search_advanced', 'lost_visions.views.do_advanced_search', name='do_advanced_search'),
                       url(r'^get_image_data', 'lost_visions.views.get_image_data', name='get_image_data'),

                       url(r'^haystack', 'lost_visions.views.haystack_search', name='haystack'),

                       url(r'^data_autocomplete', 'lost_visions.views.data_autocomplete', name='data.autocomplete'),


                       url(r'^image/tags', 'lost_visions.views.image_tags', name='image.tags'),
                       url(r'^image/alt_tags', 'lost_visions.views.get_alternative_tags', name='image.alt_tags'),

                       url(r'^image/category', 'lost_visions.views.image_category', name='image.category'),
                       url(r'^image/random', 'lost_visions.views.random_image', name='image.random'),
                       url(r'^image/grabflickr', 'lost_visions.views.grab_flickr', name='image.grab_flickr'),

                       url(r'^search_haystack/', include('haystack.urls')),

                       url(r'^oed/(?P<word>\w+)', 'lost_visions.views.oed', name='oed'),
                       url(r'^findword', 'lost_visions.views.findword', name='find.word'),

                       url(r'^find_page/(?P<book_id>\w+)/(?P<page>\w+)/(?P<volume>\w+)', 'lost_visions.views.find_page', name='find_page'),
                       url(r'^page_turner/(?P<book_id>\w+)/(?P<page>\S+)/(?P<volume>\w+)',
                           'lost_visions.views.page_turner', name='page_turner'),

                       # url(r'^categories', 'lost_visions.views.get_categories_html', name='categories_url'),
                       # url(r'^creation_techniques', 'lost_visions.views.get_creation_techniques_html', name='creation_techniques_url'),
                       # url(r'^free_text', 'lost_visions.views.free_text_html', name='free_text_description_url'),
                       # url(r'^new_tags', 'lost_visions.views.new_tags_html', name='new_tags_url'),
                       # url(r'^thank_you', 'lost_visions.views.thank_you_html', name='thank_you_url'),

                       # url('', include('social.apps.django_app.urls', namespace='social')),

                       # url(r'^blog/', include('blog.urls')),
                       # url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
                       # url(r'^admin_tools/', include('admin_tools.urls')),



)

urlpatterns += staticfiles_urlpatterns()