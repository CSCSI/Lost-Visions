import ast
import json
import logging
import os
import pprint
import requests
from random import randint, sample
import re
from types import NoneType
import urllib
import urllib2
import zipfile
from BeautifulSoup import BeautifulSoup
import StringIO
import time
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from django.contrib import auth
from django.core import serializers
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.templatetags.static import static
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
import itertools
import operator
from pygeoip import GeoIP
from crowdsource import settings
from crowdsource.settings import BASE_DIR, STATIC_ROOT, STATIC_URL, thumbnail_size, tagging_stat_min
from crowdsource.settings import ADMIN_EMAIL_ADDRESSES
from lost_visions import forms, models
from ipware.ip import get_ip
from bleach import clean
from lost_visions.categories import CategoryManager
from lost_visions.utils.page_calculator import get_page_multipliers
from lost_visions.utils.rubbish.images_for_books import get_book_images, get_images_for_flickr_id
from django.utils import timezone
logger = logging.getLogger('lost_visions')
from lost_visions.utils import db_tools
from lost_visions.utils.ImageInfo import sanitise_image_info, get_image_data_from_array, get_image_data_with_location
from lost_visions.utils.ImagePicker import ImagePicker
from lost_visions.utils.db_tools import get_next_image_id, read_tsv_file, get_thumbnail_image
from lost_visions.utils.flickr import getImageTags
from lost_visions.utils.akismet_check import is_spam
from PIL import Image
from lost_visions import mario_models

@requires_csrf_token
def home(request):
    # print request.user
    # if request.user.username:
    #     print request.user.username
    return render(request, 'home.html',
                  context_instance=RequestContext(request))

@requires_csrf_token
def get_alternative_tags(request):

    if request.method == 'POST':
        tag_info = request.POST['tag_info']
    else:
        tag_info = request.GET['tag_info']

    response_data = []
    logger.debug(tag_info)

    try:
        tags_xy = ast.literal_eval(tag_info)
        logger.debug(pprint.pformat(tags_xy))

        for tag_index in tags_xy:
            user_tag = tags_xy[tag_index]
            logger.debug(user_tag)

            # print '\n'
            # print pprint.pformat(user_tag)
            try:
                alternative_words = db_tools.list_wordnet_links(user_tag['synset'].replace(' ', '_'))[::-1]
                logger.debug('alternative_words' + str(alternative_words))

                # print 'alt_words: ' + str(alternative_words)
                alternative_words.append([user_tag['tag'], [0, 0], user_tag['synset']])

                for index, weighted_word in enumerate(alternative_words):
                    tag = {}
                    word = weighted_word[0]
                    # print 'weighted: ' + str(word)

                    tag['tag'] = clean(word, strip=True)
                    tag['synset'] = weighted_word[2]

                    tag['x_percent'] = clean(str(user_tag['x_percent']), strip=True)
                    tag['y_percent'] = clean(str(user_tag['y_percent']), strip=True)
                    # try:
                    # date_object = datetime.strptime(str(user_tag['datetime']), '%Y-%m-%dT%H:%M:%S.%f')
                    # date_object = parser.parse()
                    tag['timestamp'] = str(user_tag['timestamp'])
                    # except Exception as e3:
                    #     print e3
                    #     pass

                    received_tag_order = clean(str(user_tag['tag_order']), strip=True)
                    if len(received_tag_order) < 9:
                        tag_order = str(int(received_tag_order) * 100)

                        tag_hyp_dist = int(weighted_word[1][0]) + 1
                        tag_syn_val = int(weighted_word[1][1]) + 1
                        tag_order += str(tag_hyp_dist * 100) + str(tag_syn_val * 100)

                    else:
                        tag_order = received_tag_order

                    # print 'tag_order_weighted: ' + tag_order
                    tag['tag_order'] = str(tag_order)
                    response_data.append(tag)
            except Exception as e2:
                logger.debug('err2')
                logger.debug(e2)
                print 'get_alternative_tags.list_wordnet_links', str(e2), type(e2)
                logger.debug(('get_alternative_tags.list_wordnet_links', str(e2), type(e2)))

                pass
    except Exception as e3:
        logger.debug('err3')
        logger.debug(e3)
        print 'get_alternative_tags.literal_eval', str(e3), type(e3)
        logger.debug(('get_alternative_tags.literal_eval', str(e3), type(e3)))
        pass

    unique_comp_key = {}
    for tag in response_data:
        unique_comp_key[tag['tag'], tag['synset']] = tag

    response_data = []
    for tag_key in unique_comp_key:
        response_data.append(unique_comp_key[tag_key])

    return HttpResponse(json.dumps(response_data, indent=4), content_type="application/json")


@requires_csrf_token
def image_tags(request):
    next_action = 'next_image'
    try:
        # print request.get_full_path()

        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', {
        #     'secret': settings.captcha_secret,
        #     'response': request.POST.get('captcha_key', '')
        # })
        #
        # print r.text
        # print r.json

        if request.method == 'POST':
            next_action = clean(request.POST.get('stay_or_next_image', 'next_image'), strip=True)

            # print pprint.pformat(request.POST)
            # print request.user

            image_model = models.Image.objects.get(flickr_id=request.POST['image_id'])
            request_user = get_request_user(request)

            image_text = models.ImageText()
            image_text.caption = clean(request.POST.get('input_caption', ''), strip=True)
            image_text.description = clean(request.POST['image_description'], strip=True)
            image_text.image = image_model
            image_text.user = request_user

            if image_text.description == '' and image_text.caption == '':
                # print 'not worth saving blank image text'
                pass
            else:
                found_spam = False
                if len(image_text.description):
                    found_spam = is_spam(image_text.description)
                if len(image_text.caption):
                    found_spam = is_spam(image_text.caption)

                if not found_spam:
                    image_text.save()

            if request.POST['tag_info']:
                # and len(request.POST['tag_info'].decode('utf-8')) > 0:
                tag_info = request.POST['tag_info']
                tags_xy = ast.literal_eval(tag_info)

                # print pprint.pformat(tags_xy)

                for tag_index in tags_xy:
                    user_tag = tags_xy[tag_index]
                    try:
                        # alternative_words = db_tools.list_wordnet_links(user_tag['synset'])[::-1]
                        # alternative_words = []
                        # alternative_words.append([user_tag['tag'], [0, 0]])

                        word = clean(user_tag['tag'], strip=True)

                        if len(word) > 0:
                            # for index, weighted_word in enumerate(alternative_words):
                            tag = models.Tag()
                            # word = weighted_word[0]

                            # print word
                            tag.tag = word
                            tag.x_percent = clean(str(user_tag['x_percent']), strip=True)
                            tag.y_percent = clean(str(user_tag['y_percent']), strip=True)
                            # try:
                            # date_object = datetime.strptime(str(user_tag['datetime']), '%Y-%m-%dT%H:%M:%S.%f')
                            date_object = parser.parse(str(user_tag['timestamp']))
                            tag.timestamp = date_object
                            # except Exception as e3:
                            #     print e3
                            #     pass

                            # tag_order = str((int(clean(str(user_tag['tag_order']), strip=True)) + 1) * 100)

                            received_tag_order = clean(str(user_tag['tag_order']), strip=True)
                            if len(received_tag_order) < 9:
                                tag_order = str(int(received_tag_order) * 100) + '100100'

                                # tag_hyp_dist = int(weighted_word[1][0]) + 1
                                # tag_syn_val = int(weighted_word[1][1]) + 1
                                # tag_order += str(tag_hyp_dist * 100) + str(tag_syn_val * 100)

                            else:
                                tag_order = received_tag_order
                            tag.tag_order = str(tag_order)

                            if image_model and request_user:
                                tag.image = image_model
                                tag.user = request_user
                            tag.save()

                            try:
                                synset = clean(user_tag['synset'], strip=True)
                                if len(synset):
                                    wordnet_tag = models.WordnetTag()
                                    wordnet_tag.tag = tag
                                    wordnet_tag.wordnet_synset = synset
                                    wordnet_tag.save()
                            except:
                                pass

                    except Exception as e43533:
                        print 'error saving tags', e43533, type(e43533)
            try:
                rotate_degs = int(clean(request.POST.get('save_deg_value', 0)))
                previous_rotation_count = models.ImageRotation.objects.filter(image=image_model).count()

                if rotate_degs is not 0 or previous_rotation_count > 0:
                    rotate_model = models.ImageRotation()
                    rotate_model.rotation = int(rotate_degs)
                    rotate_model.image = image_model
                    rotate_model.user = request_user
                    rotate_model.save()
            except Exception as e329781:
                print 'rotation error', str(e329781), type(e329781)

            image_model.views_completed += 1
            image_model.save()
    except Exception as e56732:
        print 'general tag error ', str(e56732), type(e56732)

    image_id = request.POST['image_id']

    # print next_action
    if next_action == 'next_image':
        return random_image(request)
    else:
        # return image(request, image_id)
        return redirect('image', image_id=image_id)


def get_request_user(request):
    try:
        user = models.User.objects.get(username=request.user)
        lost_vision_user = models.LostVisionUser.objects.get(username=user)
        return lost_vision_user
    except Exception as e1:
        # hack using the exception to use anonymous user if not logged in
        anon_user = models.User.objects.get(username='Anon_y_mouse')
        return models.LostVisionUser.objects.get(username=anon_user)


def is_number(string):
    try:
        float(string)
        return True
    except:
        return False


def random_image(request):
    image_id = get_next_image_id()
    try:
        return redirect('image', image_id=image_id)
    except:
        raise Http404
        # print pprint.pformat(request.POST)
        # return redirect('image.random')


def is_user_tag(tag):
    # returns True if the tag is not
    # a British Library auto tag

    lowered = tag.lower()
    bl_tags = ["small", "medium", "large", "public_domain", "mechanical_curator", "bldigital"]

    if lowered in bl_tags or 'publisher' in lowered:
        return False
    else:
        return True



@requires_csrf_token
def image(request, image_id):
    try:
        image_id = clean(image_id, strip=True)
        # image_model = models.Image.objects.get(flickr_id=image_id)

        image_info = get_image_data_from_array([image_id], request)[image_id]

        # print pprint.pformat(image_info)

        # image_models = get_image_data_with_location([image_id])
        # try:
        #     image_info = db_tools.get_image_info(image_models[0])
        #     # image_info['img_small'] = get_thumbnail_image(image_models[0])
        #
        # except IndexError:
        #     return render(request, 'error.html')
        #
        # if image_info is None:
        #     image_info = dict()
        # else:
        #     image_info = sanitise_image_info(image_info, request)

        # image_info['image_area'] = int(image_info['flickr_original_height']) * int(image_info['flickr_original_width'])
        #
        # image_info['azure'] = get_tested_azure_url(image_info)
        #
        # r = requests.head(request.build_absolute_uri(static(image_info['arcca_url'])), stream=True)
        # print r
        # if r.status_code is not requests.codes.ok:
        #     if image_info['azure']:
        #         image_info['imageurl'] = image_info['azure']
        #     else:
        #         image_info['imageurl'] = image_info['flickr_url']
        # else:
        #     image_info['imageurl'] = image_info['arcca_url']

        formatted_info = dict()
        # formatted_info['Issuance'] = image_info.get('Issuance', "")
        formatted_info['Date_of_Publication'] = image_info.get('date', "")
        # formatted_info['Date_of_Publication'] = image_info.get('date', "")
        formatted_info['Title'] = image_info.get('title', "")
        formatted_info['Volume'] = image_info.get('Volume', "")
        formatted_info['Author'] = image_info.get('Author', "")
        formatted_info['Book ID'] = image_info.get('Book ID', "")
        formatted_info['Place_of_Publication'] = image_info.get('Place of Publication', "")
        # formatted_info['Place_of_Publication'] = image_info.get('Place of Publication', "")
        formatted_info['Publisher'] = image_info.get('Publisher', "")
        formatted_info['Shelfmark'] = image_info.get('Shelfmark', "")
        formatted_info['Page'] = image_info.get('page', "").lstrip('0')
        formatted_info['Identifier'] = image_info.get('flickr_id', "")

        if formatted_info['Book ID'] and formatted_info['Book ID'] != '':
            illustrator_string = ''
            illustrators = models.BookIllustrator.objects.filter(book_id=formatted_info['Book ID'])
            for illustrator in illustrators:
                illustrator_string += illustrator.name + ' (' + illustrator.technique + '),'
            if illustrator_string is not '':
                formatted_info['Illustrator(s) **'] = illustrator_string
                formatted_info['**'] = 'Data retrieved automatically from Title info, no promises'

        linked_images = models.LinkedImage.objects.filter(image__flickr_id=image_id)
        linked_image_data = []
        for link_image in linked_images:
            linked = dict()
            linked['link'] = STATIC_URL + 'media/linked_images/' + link_image.file_name
            linked['info'] = link_image.description
            linked['name'] = link_image.name
            linked_image_data.append(linked)

        # print pprint.pformat(image_info)

        image_descriptions = models.ImageText.objects.filter(image__flickr_id=image_id)
        image_descs = []
        for desc in image_descriptions:
            if len(desc.description.strip()) > 0:
                image_descs.append(desc.description)

        tags_for_image = models.Tag.objects.all().filter(image__flickr_id=image_id).values('tag') \
            .annotate(uses=Count('tag'))
        tags_for_image = list(tags_for_image)

        if settings.use_flickr:
            flickr_tags = get_flickr_tags(image_id)
            for tag in flickr_tags:
                tags_for_image.append({'tag': flickr_tags[tag], 'uses': 1, 'from_flickr': True})

        collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
        users_collections = set()
        users_collections.add('default')
        for c in collection_models:
            users_collections.add(str(c.name))
        users_collections.add('NEW COLLECTION')
        users_collections = list(users_collections)
        users_collections = sorted(users_collections, key=str.lower)

        y = 51.49006473014369
        x = -3.1805146484375
        swy = 50.49006473014369
        swx = -4.1805146484375
        ney = 52.49006473014369
        nex = -2.1805146484375

        image_model = models.Image.objects.get(flickr_id=image_id)
        rotate_models = models.ImageRotation.objects.filter(image=image_model).order_by('timestamp')

        rotation = 0
        if rotate_models.count():
            rotation = int(rotate_models.reverse()[0].rotation)


        image_info['imageurl'] = image_info.get('img', '')
        return render(request, 'image.html',
                      {'image': image_info,
                       'book_id': image_info.get('book_id', ""),
                       'volume': image_info.get('volume', ""),
                       'page': image_info.get('page', ""),
                       'formatted_info': formatted_info,
                       'image_id': image_id,
                       'image_tags': json.dumps(list(tags_for_image)),
                       # 'category_data': category_data,
                       'user_collections': users_collections,
                       'linked_images': linked_image_data,
                       'image_descriptions': image_descs,
                       'rotation': rotation,

                       'x': x,
                       'y': y,
                       'ne_x': nex,
                       'ne_y': ney,
                       'sw_x': swx,
                       'sw_y': swy,

                       'this_url': reverse('image', kwargs={'image_id': image_id})},
                      context_instance=RequestContext(request))
    except:
        raise Http404


def get_flickr_tags(image_id):

    # try:

    #cut image ID from image URL
    #get Flickr tags for this image
    flickr_tags = getImageTags('http://www.flickr.com/photos/britishlibrary/' + image_id, size='z')
    author = u''
    if u'Author' in flickr_tags:
        # print "found author : " + flickr_tags['Author']
        author = flickr_tags['Author']

    # if not 'imageurl' in image_info and 'image_location' in flickr_tags:
    #     image_info['imageurl'] = flickr_tags['image_location']

    tags = {}
    for tag in flickr_tags:

        # print '\n'
        # print tag
        # print type(flickr_tags[tag])
        # print flickr_tags[tag]
        #
        # print type(author)
        # print author

        if is_number(tag) and is_user_tag(flickr_tags[tag]):

            # print "*" + str(flickr_tags[tag]).lower() + "* *" + str(author).lower() + "*"

            if flickr_tags[tag].lower().strip() != author.lower().strip():



                # try:
                #     #     # TODO utf fix
                #     print "*" + flickr_tags[tag].lower() + "* *" + author.lower() + "*"
                # except Exception as e:
                #     print e


                tags[tag] = flickr_tags[tag]
        else:
            # image_info[tag] = flickr_tags[tag].replace('&quot;', '"')
            pass

    return tags

    # except Exception as e:
    #     print 'flickr access error : ' + str(e)
    # return {}


def get_creation_techniques_html(request):
    CreationTech = forms.creation_technique_form_factory()
    create_tech = CreationTech()

    return render(request, 'divs/creation_techniques.html', {'create_tech_form': create_tech})


def get_categories_html(request):
    CategoryForm = forms.category_form_factory()
    category_form = CategoryForm()

    return render(request, 'divs/categories.html', {'category_form': category_form})


def random_file_in_folder(folder):
    files = []
    for a_file in os.listdir(folder):
        full_path = os.path.join(folder, a_file)
        if os.path.isfile(full_path):
            files.append( full_path )
    file_number = randint(0, len(files))
    return files[file_number]


def random_line_number(filename):
    lines = 0
    for _ in open(filename):
        lines += 1
    # print 'there are ' + str(lines) + ' lines'
    return randint(1,lines)


def get_random_image_data():
    random_file = random_file_in_folder('/home/ubuntu/flickr_files/imagedirectory/')
    # print random_file
    line_number = random_line_number(random_file)
    # print 'getting line ' + str(line_number)
    return read_tsv_file(random_file, line_number)


def grab_flickr(request):

    if request.method == 'POST':
        CategoryForm = forms.category_form_factory()
        form = CategoryForm(request.POST)
        if form.is_valid():
            print 'valid form'
        else:
            print 'invalid form'

        categories = ["cycling",
                      "cover",
                      "castle",
                      "decorative papers",
                      "ship",
                      "technology",
                      "sciencefiction",
                      "children's book illustration",
                      "letter",
                      "decoration",
                      "map",
                      "fashion",
                      "portrait",
                      "christmas"]
        for cat in categories:
            if cat in form.cleaned_data:
                print cat

    # assume a problem !!!
    problem = True
    # loop to prefer failing than looping forever
    loop = 0
    while problem and loop < 20:
        loop+=1
        print str(loop)
        image_data = get_random_image_data()
        if image_data is not None:
            if 'flickr_id' in image_data:
                # this is all we care about for now
                problem = False
    return image(request, image_data['flickr_id'])


def free_text_html(request):
    return render(request, 'divs/free_text_description.html')


def new_tags_html(request):
    return render(request, 'divs/new_tags.html')


def thank_you_html(request):
    return render(request, 'divs/thank_you.html')


def aboutus(request):
    return render(request, 'about_us.html', context_instance=RequestContext(request))

@requires_csrf_token
def login(request):
    return render(request, 'login.html',
                  context_instance=RequestContext(request))

@requires_csrf_token
def do_signup(request):
    # print request.POST
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            print("User is valid, active and authenticated")
            auth.login(request, user)
            success = True
            msg = 'You have successfully logged in'
        else:
            print("The password is valid, but the account has been disabled!")
            success = False
            msg = 'This account has been disabled. Please contact the Lost-Visions team.'

        return render(request, 'home.html',
                      {'login_success': success, 'msg': msg},
                      context_instance=RequestContext(request))
    else:
        msg = 'Username and Password combination not recognised, please try again.'
        success = False

        return render(request, 'login.html',
                      {'login_success': success, 'msg': msg},
                      context_instance=RequestContext(request))

@requires_csrf_token
def do_login(request):

    # print request.POST
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            print("User is valid, active and authenticated")
            auth.login(request, user)
            success = True
            msg = 'You have successfully logged in'
        else:
            print("The password is valid, but the account has been disabled!")
            success = False
            msg = 'This account has been disabled. Please contact the Lost-Visions team.'

        return render(request, 'home.html',
                      {'login_success': success, 'msg': msg},
                      context_instance=RequestContext(request))
    else:
        msg = 'Username and Password combination not recognised, please try again.'
        success = False

        return render(request, 'login.html',
                      {'login_success': success, 'msg': msg},
                      context_instance=RequestContext(request))

@requires_csrf_token
def logout(request):
    logout_success = False
    msg = 'Auth Error, please refresh the page'
    if request.user.is_authenticated():
        auth.logout(request)
        msg = 'You have successfully logged out'
        logout_success = True
    #do logout
    return render(request, 'home.html',
                  {'logout_success': logout_success, 'msg': msg},
                  context_instance=RequestContext(request))


@requires_csrf_token
def signup(request):
    return render(request, 'signup.html', context_instance=RequestContext(request))


@requires_csrf_token
def oed(request, word):

    # url = 'http://www.oed.com/srupage?operation=searchRetrieve&query=cql.serverChoice+=+'
    # url += word
    # url += '*&maximumRecords=100&startRecord=1'

    url = 'http://localhost:8000/static/oed.xml'
    print url
    resp = urllib2.urlopen(url)

    words = []
    if resp.code == 200:
        data = resp.read()

        print data
        xml = BeautifulSoup(data)

        for elm in xml.findAll('srw:searchretrieveresponse'):
            for div in elm.findAll('srw:records'):
                for a in div.findAll('srw:record'):
                    for img in a.findAll('srw:recorddata'):
                        for record_dc in img.findAll('sru_dc:dc'):
                            for title in record_dc.findAll('dc:title'):
                                # print '*' + str(title.text) + '*'
                                # if "n." == title.text.split()[-1]:
                                if 'in ' + word + ',' not in title.text:
                                    print title.text
                                    words.append(title.text)
    response_data = words

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@requires_csrf_token
def findword(request):

    word = request.GET['term']

    response_data = db_tools.wordnet_formatted(word)

    return HttpResponse(json.dumps(response_data, indent=4), content_type="application/json")


def record_search(request, word):

    ip = get_ip(request)
    if ip is not None:
        print "we have an IP address for user"
        print ip
        g = GeoIP(os.path.join(BASE_DIR, 'GeoLiteCity.dat'))
        location = g.record_by_addr(ip)
        print word
        print str(location)
    else:
        print "we don't have an IP address for user"

    pass


@requires_csrf_token
def search(request, word):
    results = dict()
    total_results = 0

    word = clean(word, strip=True)

    record_search(request, word)

    search_result = models.SearchQuery()
    search_result.user = get_request_user(request)
    search_result.search_term = word
    search_result.save()

    results['tag'] = dict()
    results['author'] = dict()
    results['caption'] = dict()
    for subword in word.split('+'):

        tag_results = models.Tag.objects.order_by('-image__views_begun').filter(
            Q( tag__icontains=subword ))[:30]

        tag_results_dict = dict()
        for result in tag_results:
            tag_result = dict()
            tag_result['tag'] = result.tag
            tag_result['title'] = result.image.title
            tag_result['img'] = result.image.flickr_small_source

            tag_results_dict[result.image.flickr_id] = tag_result
            total_results += 1

            #increment the views so the next search skips this one
            result.image.views_begun +=1
            result.image.save()

        results['tag'].update(tag_results_dict)


        caption_results = models.ImageText.objects.order_by('-image__views_begun').filter(
            Q( caption__icontains=subword ) | Q( description__icontains=subword ))[:30]

        caption_results_dict = dict()
        for result in caption_results:
            caption_result = dict()
            caption_result['caption'] = result.caption
            caption_result['title'] = result.image.title
            caption_result['img'] = result.image.flickr_small_source
            caption_result['description'] = build_substring(subword, result.description, 6)

            caption_results_dict[result.image.flickr_id] = caption_result
            total_results += 1

            result.image.views_begun +=1
            result.image.save()

        results['caption'].update(caption_results_dict)


        author_results = models.Image.objects.order_by('-views_begun').filter(
            Q(first_author__icontains=subword) | Q(title__icontains=subword))[:30]

        author_results_dict = dict()
        for result in author_results:
            tag_result = dict()
            tag_result['author'] = result.first_author
            tag_result['title'] = result.title
            tag_result['img'] = result.flickr_small_source

            #produce a substring of the title containing the search term, approx 6 words long
            tag_result['search_substring'] = build_substring(subword, tag_result['title'], 6)

            author_results_dict[result.flickr_id] = tag_result
            total_results += 1
            result.views_begun +=1
            result.save()
        results['author'].update(author_results_dict)

    response_data = {'results': results, 'size': total_results, 'search_string': word.replace('+', ' OR ')}

    return render(request, 'results.html',
                  {'results': response_data},
                  context_instance=RequestContext(request))


# method to find the search term in the string
# produces a substring containing the term
# adds html strong tag around the search term
# returned string approx 'length' words long, less if array is too short
def build_substring(word, long_string, length):
    title_arr = long_string.split()
    word_pos = word_in_word(word, title_arr)

    if word_pos == -1:
        return ''
    else:
        start_pos = word_pos - int(length / 2)

        substring_array = title_arr[start_pos:start_pos+length]

        substring = ' '.join(substring_array)
        return insert_bold(substring, word)


#regex search ton find term, case insensitive
#add html strong tag
def insert_bold(string, word_to_bold):
    str_arr = re.compile(word_to_bold, re.IGNORECASE).split(string)
    str_arr[0] = str_arr[0] + '<strong>' + word_to_bold + '</strong>'
    return ''.join(str_arr)


# finds if search term is a substring of an individual word
# eg search term 'bone'. 'Marylebone' contains the word 'bone',
# so return index for 'Marylebone'
def word_in_word(string, word_array):
    for index, word in enumerate(word_array):
        if string.lower() in word.lower():
            return index
    return -1


@requires_csrf_token
def map(request, image_id):
    # print 'map for image : ' + image_id

    y = 51.49006473014369
    x = -3.1805146484375
    swy = 50.49006473014369
    swx = -4.1805146484375
    ney = 52.49006473014369
    nex = -2.1805146484375

    # print request.GET

    if request.GET.get('x', 10000) is not 10000:
        x = request.GET.get('x')

    if request.GET.get('y', 10000) is not 10000:
        y = request.GET.get('y')

    if request.GET.get('nex', 10000) is not 10000:
        nex = float(request.GET.get('nex'))

    if request.GET.get('ney', 10000) is not 10000:
        ney = float(request.GET.get('ney'))

    if request.GET.get('swx', 10000) is not 10000:
        swx = float(request.GET.get('swx'))

    if request.GET.get('swy', 10000) is not 10000:
        swy = float(request.GET.get('swy'))

    if nex == swx:
        nex = float(nex) + 0.05
        swx = float(swx) - 0.05

    if ney == swy:
        ney = float(ney) + 0.05
        swy = float(swy) - 0.05

    return render(request,
                  'image_map.html',
                  {'image_id': image_id,
                   'x': x,
                   'y': y,
                   'ne_x': nex,
                   'ne_y': ney,
                   'sw_x': swx,
                   'sw_y': swy
                   },
                  context_instance=RequestContext(request))


def coords_save(request):
    # print image_id
    # print request.POST

    # print request.POST['north_east_x']
    # print request.POST['north_east_y']
    # print request.POST['south_west_x']
    # print request.POST['south_west_y']

    try:
        geotag = models.GeoTag()
        if request.POST['north_east_x']:
            geotag.north_east_x = request.POST['north_east_x']
        if request.POST['north_east_y']:
            geotag.north_east_y = request.POST['north_east_y']
        if request.POST['south_west_x']:
            geotag.south_west_x = request.POST['south_west_x']
        if request.POST['south_west_y']:
            geotag.south_west_y = request.POST['south_west_y']
        geotag.image = models.Image.objects.get(flickr_id=request.POST['image_id'])
        geotag.user = get_request_user(request)

        geotag.save()
    except Exception as e:
        print 'coords_save err', str(e), type(e)

    result = {'success': True}
    return HttpResponse(json.dumps(result), content_type="application/json")



@requires_csrf_token
def coords(request, image_id):

    coords_save(request)

    return map(request, image_id)


@requires_csrf_token
def save_image(request):
    if request.is_ajax():
        if request.POST.get('delete_image', False):
            # try:
            #     # TODO this can go soon
            #     delete_image = models.SavedImages.objects.get(image__flickr_id=request.POST['image_id'])
            #     delete_image.delete()
            # except Exception as e:
            #     print e

            try:
                # TODO use this from now on
                c_id = request.POST['collection_id']
                collection = models.ImageCollection.objects.get(id=c_id, user=get_request_user(request))

                saved_image = models.ImageMapping.objects.get(collection=collection, image__flickr_id=request.POST['image_id'])
                saved_image.delete()
            except Exception as e:
                print 'delete_image error', str(e), type(e)

            return HttpResponse('Removed Image ' + request.POST['image_id'])
        else:
            try:
                user = get_request_user(request)
                image = models.Image.objects.get(flickr_id=request.POST['image_id'])

                if user and image and user.username.username is not 'Anon_y_mouse':
                    image_to_save = models.SavedImages.objects.get_or_create(user=user, image=image)

                    return HttpResponse('Saved Image ' + request.POST['image_id'])
            except Exception as e:
                print 'save_image error', str(e), type(e)
                return HttpResponse('Error')
    else:
        raise Http404


@requires_csrf_token
def user_home(request):
    if request.user.is_authenticated():

        request_user = get_request_user(request)

        saved_images = models.SavedImages.objects.filter(user=request_user)

        saved_images_dict = dict()
        for image in saved_images:

            image_dict = dict()
            image_dict['title'] = image.image.title
            image_dict['page'] = image.image.page.lstrip('0')
            image_dict['url'] = image.image.flickr_small_source

            saved_images_dict[image.image.flickr_id] = image_dict

            # TODO : remove this once users have switched over to multiple collection system
            try:
                collection, created = models.ImageCollection.objects.get_or_create(name='default', user=request_user)
                saved_image, created = models.ImageMapping.objects.get_or_create(collection=collection, image=image.image)
            except Exception as e:
                print e

        metrics = dict()
        metrics['user_tags_number'] = models.Tag.objects.filter(user=request_user).count()
        metrics['user_tagged_image_number'] = models.Tag.objects.filter(user=request_user) \
            .values('image__id').distinct().count()

        metrics['total_tags_number'] = models.Tag.objects.count()
        metrics['total_tagged_image_number'] = models.Tag.objects.values('image__id').distinct().count()

        collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
        users_collections = dict()

        for c in collection_models:

            collection_data = {}
            mapped_images = models.ImageMapping.objects.filter(collection=c)
            mapped_images_array = []

            mapped_images_size = mapped_images.count()

            mapped_image_ids = []
            for mapped_image in mapped_images[:2]:
                mapped_image_ids.append(mapped_image.image.flickr_id)
            all_image_data = get_image_data_from_array(mapped_image_ids, request)

            for image in mapped_images[:2]:
                image_dict = dict()
                image_dict['flickr_id'] = image.image.flickr_id
                image_dict['title'] = image.image.title
                image_dict['page'] = image.image.page.lstrip('0')
                image_dict['url'] = image.image.flickr_small_source

                try:
                    image_mapping_caption = models.SavedImageCaption.objects.get(image_mapping=image)
                    image_dict['caption'] = image_mapping_caption.caption

                    all_image_data.get(image.image.flickr_id)['caption'] = image_mapping_caption.caption
                except Exception as e:
                    pass
                    # print e

                mapped_images_array.append(image_dict)

            collection_data['restricted_size'] = mapped_images_size > 15
            collection_data['images'] = mapped_images_array
            collection_data['collection_size'] = mapped_images_size
            # collection_data['images_with_locations'] = all_image_data
            collection_data['collection_name'] = c.name

            users_collections.update({str(c.id): collection_data})


        return render(request,
                      'user_home.html',
                      {'images': saved_images_dict,
                       'users_collections': users_collections,
                       'metrics': metrics})
    else:
        raise Http404

ICON_URL = STATIC_URL + 'media/images/icon/'


category_manager = CategoryManager()


# OK, this needs explaination
# category_manager above stores the category "tree"
# not really a tree, as linkages can go between anything and anything
def image_category(request):
    # print request.POST

    # get the ID for the category just clicked
    # if no cat_id then default to root ID of -1
    cat_id = request.POST.get('category_id', '-1')

    # request_user = get_request_user(request)
    try:
        #     #
        image_id = request.POST.get('image_id', None)
        # image_model = models.Image.objects.get(flickr_id=request.POST['image_id'])
        if image_id is not None:

            # TODO this is messy
            # Update the map-page link and other Action links
            # This will change as we're using dialogs instead of new tabs
            category_manager.update_image_actions(image_id)

            # Get the category name for the id
            # name is returned if available and should_save is True
            # this is the word which gets saved as a tag

            # category_name = category_manager.get_tag_for_category_id(cat_id)

            # if category_name is not None:
            # tag = models.Tag()
            # tag.tag = category_name
            # tag.image = image_model
            # tag.user = request_user
            # tag.timestamp = datetime.now(tzlocal())
            # tag.tag_order = 0
            # tag.save()

            # text_entry = request.POST.get('text_entry', '')
            # if len(text_entry):
            #     tag = models.Tag()
            #     tag.tag = text_entry
            #     tag.image = image_model
            #     tag.user = request_user
            #     tag.timestamp = datetime.now(tzlocal())
            #     tag.tag_order = 0
            #     tag.save()

    except Exception as e:
        print 'image_category', str(e), type(e)
        pass

    # get data for the clicked category
    # defines the buttons etc which should be shown next
    category_data = category_manager.get_category_data(cat_id)

    return HttpResponse(json.dumps(category_data), content_type="application/json")


def search_advanced(request):
    return render(request, 'search_advanced.html', {}, context_instance=RequestContext(request))


def do_advanced_search(request):

    number_of_results_int = 50
    max_results = settings.MAX_RESULTS

    # tk = TimeKeeper()
    # tk.time_now('start')

    keywords = request.GET.get('keyword', '')
    number_of_results = request.GET.get('num_results', '')

    year_from = request.GET.get('date_from', '').strip()
    year_to = request.GET.get('date_to', '').strip()

    results = dict()
    results['advanced'] = dict()
    total_results = 0

    results['collections'] = []

    readable_query = ''
    all_image_ids = ''

    if number_of_results is not '':
        try:
            number_of_results_int = int(number_of_results)
        except:
            pass
    readable_query += 'Showing first ' + str(number_of_results_int) + ' results '

    books_in_date_range = None
    # print year_from, year_to
    if len(year_from) and year_from is not '--' and len(year_to) and year_to is not '--':
        date_range = [year_from + '-01-01', year_to + '-12-31']
        books_in_date_range = models.Book.objects.filter(datetime__range=date_range).values_list('book_identifier', flat=True)

        print 'books in range', date_range, books_in_date_range.count()
        print 'books_in_date_range.query', books_in_date_range.query

        # logger.debug('books in range ' + str(year_from) + ' ' + str(year_to) + ' : ' + str(books_in_date_range.count()))
        # logger.debug(books_in_date_range)
        # ors = [SQ(book_identifier=str(x)) for x in books_in_date_range]
        # if len(ors):
        #     all_results = all_results.filter(reduce(operator.or_, ors))

    im = ImagePicker()
    alternative_search = request.GET.get('alternative_search', '')
    too_many = False

    # tk.time_now('start search')

    if alternative_search is '':
        all_results = im.advanced_search(request)

        # tk.time_now('search done, begin sort')

        if all_results.count() > max_results:
            too_many = True

        # tk.time_now('counted results')

        if not too_many:
            # tk.time_now('begin id join')

            to_join = []
            for result in all_results:
                # logger.debug(len(django.db.connection.queries))
                to_join.append(result)
                # total_results += 1
                # all_image_ids += result + ','

            # tk.time_now('got id list')
            all_image_ids = ','.join(to_join)
            total_results = len(all_results)
            readable_query += '(over ' + str(len(all_results)) + ' found)'

            # tk.time_now('finish id join')
        else:
            readable_query += 'Please add more detail to the query. '

            for result in all_results[:max_results]:
                total_results += 1
                all_image_ids += result + ','
            readable_query += 'Only returning first ' + \
                              str(max_results) + \
                              ' images of (' + str(len(all_results)) + ' found)'

            # tk.time_now('done search')
    else:
        all_results_haystack = im.advanced_haystack_search(request.GET, book_ids=books_in_date_range).load_all()
        # print 'all_results_haystack', all_results_haystack.count()

        user = get_request_user(request)
        logger.debug(str(user.username.username) + " : " + pprint.pformat(request.GET))

        # print all_results_haystack.query
        # print all_results_haystack.count()
        # distincts = all_results_haystack.values_list('flickr_id', flat=True)
        # print len(distincts)
        #
        # unique_set = set()
        # for o in flickr_id_list_from_searchqueryset(distincts):
        #     unique_set.add(o)
        # print len(unique_set)

        # tk.time_now('search done, begin sort')

        # print all_results_haystack
        # print type(all_results_haystack)

        # # TODO check if this block is needed now
        # to_join = []
        # try:
        #     for x in all_results_haystack[:max_results]:
        #         # print x.flickr_id
        #         # print pprint.pformat(x.__dict__.get('flickr_id'))
        #         # all_image_ids += x.flickr_id + ','
        #         try:
        #             if type(x) is not NoneType and x.flickr_id not in to_join:
        #                 if len(books_in_date_range):
        #                     if x.book_identifier in books_in_date_range:
        #                         to_join.append(x.flickr_id)
        #                 else:
        #                     to_join.append(x.flickr_id)
        #         except:
        #             pass
        # except Exception as e23458:
        #     print str(e23458)
        #     pass

        to_join = get_images_in_books(all_results_haystack, books_in_date_range, max_results)

        # all_results = [x.object for x in all_results_haystack]
        if len(to_join) > 0:
            all_image_ids = ','.join(to_join)

        # tk.time_now('pulled search objects')

        # result_count = all_results_haystack.count()
        result_count = len(to_join)

        # for o in all_results[:5000]:
        # if type(o) == Image:
        #     # print 'image\n'
        #     total_results += 1
        #     all_image_ids += o.flickr_id + ','
        #
        # if type(o) == Tag:
        #     # print 'tag\n'
        #     total_results += 1
        #     all_image_ids += o.image.flickr_id + ','
        #
        # if type(o) == ImageText:
        #     # print 'text\n'
        #     total_results += 1
        #     all_image_ids += o.image.flickr_id + ','

        # tk.time_now('pulled image_ids')

        if result_count > (max_results - 1):
            #            too_many = True
            # readable_query += 'Please add more detail to the query. '
            readable_query += 'Only returning first ' + str(max_results) + ' images of (' + str(result_count) + ' found)'
        else:
            readable_query += ' of ' + str(result_count) + ' found.'

            # tk.time_now('done alt search')
    results['advanced'] = []

    response_data = {'results': results, 'size': total_results, 'search_string': keywords}

    user_collections = []
    if request.user.is_authenticated():
        collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
        for model in collection_models:
            user_collections.append({'name': model.name,
                                     'id': str(model.id)})

    # Get collections
    found_collection_models = im.find_collections(request.GET)
    found_collections = []
    if found_collection_models.count() > 0:
        for collection_model in found_collection_models:

            image_mapping_set = collection_model.imagemapping_set.all()
            if image_mapping_set.count() > 0:

                image_datas = get_image_data_from_array([image_mapping_set[0].image.flickr_id], request)
                image_url = ''
                for img_data_id, img_data in image_datas.items():
                    image_url = img_data['img_small']

                found_collections.append({
                    'collection_name': collection_model.name,
                    'collection_size': collection_model.imagemapping_set.all().count(),
                    'collection_id': collection_model.id,
                    'collection_creator': get_collection_creator(collection_model),
                    'image_url': image_url
                })

    results['collections'] = found_collections

    return render(request, 'advanced_search_results.html',
                  {'results': response_data,
                   'query_array': request.GET,
                   'query': readable_query,
                   'all_image_ids': all_image_ids,
                   'number_to_show': number_of_results_int,
                   'user_collections': user_collections},
                  context_instance=RequestContext(request))


def get_images_in_books(images, books, max_results):
    # These are the images returned from haystack
    # We need to filter by which books we're allowing
    # Books are selected using a date range
    # This avoids solr throwing "too many boolean clauses" when filtering multiple years
    # Also allows specific tailoring of max_results we're allowing, tweak till reasonable timings

    # logger.debug('checking if {} are in {} books'.format(images.count(), len(books)))

    # print 'checking if ', images.count(), 'are in ', len(books), 'books'

    # book_filtered = models.Image.objects.all()
    if books is None:
        return images.values_list('flickr_id', flat=True)[:max_results]

    if len(books) == 0:
        # If we have no valid books in the age range, then no images are valid. Return empty set
        return set()

    else:
        # If we specify books, we're looking in them only
        # Otherwise return all images

        # book_filtered = book_filtered.filter(
        #     book_identifier__in=books
        # )

        filtered_images = images.filter(
            book_identifier__in=books[:settings.MAX_BOOK_RESULTS]
        )
        print 'filtered_images1', filtered_images.count(), max_results

        # a = 0
        # b = 1024
        # c = 0
        # while c < max_results and b < len(books):
        #     a += 1024
        #     b += 1024
        #     print a, b, c, max_results
        #
        #     this_bookset = books[a:b]
        #     print len(this_bookset)
        #     print type(this_bookset)
        #
        #     this_set = images.filter(
        #         book_identifier__in=this_bookset
        #     )
        #     print 'this_set', this_set.count()
        #
        #     filtered_images = filtered_images | this_set
        #     c += this_set.count()

        book_filtered = filtered_images

    # logger.debug('book_filtered.count {}'.format(book_filtered.count()))

    # print 'book_filtered.count()', book_filtered.count()

    # book_filtered = book_filtered.filter(
    #     flickr_id__in=images.values_list('flickr_id', flat=True)[:max_results]
    # ).values_list(
    #     'flickr_id', flat=True
    # ).distinct()

    # print 'book_filtered.query', book_filtered.query
    book_filtered = book_filtered.values_list('flickr_id', flat=True)[:max_results]
    book_filtered = set(book_filtered)
    return list(book_filtered)


def flickr_id_list_from_searchqueryset(sqs):
    for thing in sqs:
        yield thing


def data_autocomplete(request):
    # print request.GET

    term = request.GET['term']

    response_data = []

    if request.GET['data_object'] == 'author':
        all_authors = models.Image.objects.filter(Q(first_author__icontains=term)) \
            .order_by('first_author').values_list('first_author').distinct()
        for author in all_authors:
            word_data = dict()
            word_data['label'] = author[0]
            word_data['desc'] = 'author'
            response_data.append(word_data)

    if request.GET['data_object'] == 'illustrator':
        all_illustrators = models.BookIllustrator.objects.filter(name__icontains=term) \
            .order_by('name').values_list('name').distinct()
        for illustrator in all_illustrators:
            word_data = dict()
            word_data['label'] = illustrator[0]
            word_data['desc'] = 'illustrator'
            response_data.append(word_data)

    if request.GET['data_object'] == 'title':
        all_authors = models.Image.objects.filter(Q(title__icontains=term)) \
            .order_by('title').values_list('title').distinct()
        for author in all_authors:
            word_data = dict()
            word_data['label'] = author[0]
            word_data['desc'] = 'title'
            response_data.append(word_data)

    if request.GET['data_object'] == 'publisher':
        all_publishers = models.Image.objects.filter(Q(publisher__icontains=term)) \
            .order_by('publisher').values_list('publisher').distinct()
        for publisher in all_publishers:
            word_data = dict()
            word_data['label'] = publisher[0]
            word_data['desc'] = 'publisher'
            response_data.append(word_data)

    if request.GET['data_object'] == 'publishing_place':
        all_publishing_places = models.Image.objects.filter(Q(pubplace__icontains=term)) \
            .order_by('pubplace').values_list('pubplace').distinct()
        for pubplace in all_publishing_places:
            word_data = dict()
            word_data['label'] = pubplace[0]
            word_data['desc'] = 'Place of Publishing'
            response_data.append(word_data)
    return HttpResponse(json.dumps(response_data), content_type="application/json")




def get_resized_image(request, book_identifier, volume, page, image_idx):

    response = HttpResponse(content_type="image/jpeg")
    filename = str(book_identifier + '.' + volume + '.' + page + '.' + image_idx)
    try:
        image_location = models.ImageLocation.objects.filter(book_id=book_identifier,
                                                             volume=volume,
                                                             page=page,
                                                             idx=image_idx)
        if len(image_location):


            img = Image.open(image_location[0].location)
            # print image_location[0].location
            # img.verify()

            basewidth = thumbnail_size
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))

            img.thumbnail((basewidth, hsize), Image.ANTIALIAS)
            # response['Content-Disposition'] = 'attachment; filename=%s' % filename
            img.save(response, "JPEG", quality=80, optimize=True, progressive=True)
        else:
            raise
    except:
        raise Http404
    return response


def get_image_data(request):

    ids = request.POST.get('image_ids', '')
    if ids == '':
        ids = request.GET.get('image_ids', '')
    tag_results_dict = dict()

    if ids:
        id_list = ids.split(',')

        tag_results_dict = get_image_data_from_array(id_list, request)

    return HttpResponse(json.dumps(tag_results_dict), content_type="application/json")


def user_dl_all(request):
    # print request.GET

    collection_ids = request.GET.get('collection_ids')

    # print collection_ids
    if collection_ids:
        # collection_list = ast.literal_eval(collection_ids)
        collection_list = collection_ids.split(',')

        filenames = dict()
        for image_id in collection_list:
            image_model = models.Image.objects.get(flickr_id=image_id)
            image_info = db_tools.get_image_info(image_model)

            if image_info:
                filenames[image_id] = (image_info['imageurl'])

        # Files (local path) to put in the .zip
        # FIXME: Change this (get paths from DB etc)
        # filenames = ["/tmp/file1.txt", "/tmp/file2.txt"]

        # Folder name in ZIP archive which contains the above files
        # E.g [thearchive.zip]/somefiles/file2.txt
        # FIXME: Set this to something better
        zip_subdir = 'bl_images'
        zip_filename = "%s.zip" % zip_subdir

        # Open StringIO to grab in-memory ZIP contents
        s = StringIO.StringIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)

        for image_id in filenames:

            fpath = filenames[image_id].replace(' ', '%20')

            filename = os.path.join('/tmp/', image_id + '.jpg')
            if 'static/media' in fpath:
                fpath = 'http://illustrationarchive.cf.ac.uk' + fpath
            urllib.urlretrieve(fpath, filename)
            fpath = filename

            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)

            # Add file, at correct path
            zf.write(fpath, zip_path)

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

        return resp
    else:
        return redirect('user_profile_home')


def get_stats():
    tags_for_image = models.Tag.objects.all().values('tag').annotate(uses=Count('tag')).filter(uses__gt=tagging_stat_min)
    u = 1
    most_used_tag = ''
    for v in list(tags_for_image):
        if v['uses'] > u:
            u = v['uses']
            most_used_tag = v['tag']

    metrics = dict()
    metrics['total_tags_number'] = models.Tag.objects.count()
    metrics['total_tagged_image_number'] = models.Tag.objects.values('image__id').distinct().count()
    data = {
        'metrics': metrics,
        'image_tags': list(tags_for_image),
        'most_used_tag_count': u,
        'most_used_tag': most_used_tag
    }
    return data


def stats_json(request):
    return HttpResponse(json.dumps(get_stats(), indent=4), content_type="application/json")


def stats(request):
    data = get_stats()
    return render(request, 'stats.html', data, context_instance=RequestContext(request))


def haystack_search(request):
    query_response = {'hello': 'world', 'test': ['a', 'b', 3], 'the_request': request.GET}

    im = ImagePicker()

    to_filter = request.GET

    found_imagepicker = im.advanced_haystack_search(to_filter)

    rl = [x.object for x in found_imagepicker]

    results_list_ser = serializers.serialize('json', rl)

    query_response['image_picker'] = json.loads(results_list_ser)

    # keys = [x.object.__dict__.get('flickr_id') for x in found_imagepicker]
    keys = [x.object.flickr_id for x in found_imagepicker]


    # print keys

    query_response['list'] = keys

    # mlt = SearchQuerySet().more_like_this(Image.objects.get(flickr_id=keys[0]))
    #
    # mlt_objects = [x.object for x in mlt]
    #
    # mlt_objects_ser = serializers.serialize('json', mlt_objects)
    #
    # query_response['mlt'] = json.loads(mlt_objects_ser)
    # query_response['mlt_count'] = mlt.count()

    return HttpResponse(json.dumps(query_response, indent=4), content_type="application/json")


def download_collection(request):
    collection_id = request.GET.get('collection_id')

    image_collection = models.ImageCollection.objects.all().get(id=collection_id)

    images = models.ImageMapping.objects.filter(collection=image_collection)

    image_ids = []
    for image_mapping in images:
        image_ids.append(image_mapping.image.flickr_id)

    filenames = dict()
    for image_id in image_ids:
        image_model = models.Image.objects.get(flickr_id=image_id)
        image_info = db_tools.get_image_info(image_model)
        image_info = sanitise_image_info(image_info, request)

        if image_info:
            filenames[image_id] = (image_info['imageurl'])

    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    # filenames = ["/tmp/file1.txt", "/tmp/file2.txt"]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = image_collection.name
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    # .ZIP_STORED .ZIP_DEFLATED
    zf = zipfile.ZipFile(s, "w", zipfile.ZIP_STORED)

    for image_id in filenames:

        fpath = filenames[image_id].replace(' ', '%20')

        filename = os.path.join('/tmp/', image_id + '.jpg')
        if 'static/media' in fpath:
            fpath = 'http://illustrationarchive.cf.ac.uk' + fpath
        urllib.urlretrieve(fpath, filename)
        fpath = filename

        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

        image_info = get_image_data_dict(image_id)

        json_path = os.path.join(zip_subdir, str(image_id) + '.json')
        zf.writestr(json_path, json.dumps(image_info, indent=4))

        try:
            chicago_path = os.path.join(zip_subdir, str(image_id) + '-chicago-formatted.txt')

            formatted_data = 'Illustration. '
            bl_data = image_info['bl_flickr_data'][0]['fields']

            formatted_data += str(bl_data['flickr_original_height']) + ' ' + str(bl_data['flickr_original_height']) + ' px. '
            formatted_data += 'From ' + str(bl_data['title']) + ' ' + str(bl_data['first_author']) + '. '

            zf.writestr(chicago_path, formatted_data)
        except:
            pass

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp
    # return redirect('user_profile_home')


def get_api_key(request):
    request_user = get_request_user(request)
    apikey = get_random_string(length=64)
    valid_to = datetime.today() + relativedelta(months=1)

    api_model = models.APIkey()
    api_model.api_key = apikey
    api_model.user = request_user
    api_model.valid_to = valid_to
    api_model.save()

    return HttpResponse(json.dumps({
        'user': request_user.username.username,
        'api_key': apikey,
        'valid_till': valid_to.strftime('%Y-%m-%d %H:%M:%S %Z')}, indent=4), content_type="application/json")


def auth_api_key(api_key):
    try:
        users_api_key = models.APIkey.objects.get(api_key=api_key)
        user_model = users_api_key.user
        today = datetime.today().replace(tzinfo=timezone.utc)
        valid_to = users_api_key.valid_to

        success = valid_to > today
        time_remaining = str(valid_to - today)
        valid_till = valid_to.strftime('%Y-%m-%d %H:%M:%S %Z')

        return success, time_remaining, valid_till, None, user_model

    except Exception as e83274:
        success = False
        return success, None, None, str(e83274), None


def is_valid_api_key(request):

    apikey = request.GET.get('api_key', '')
    request_user = get_request_user(request)

    anon_user = models.User.objects.get(username='Anon_y_mouse')
    anon_lv_model = models.LostVisionUser.objects.get(username=anon_user)

    return_object = {}
    return_object['user'] = request_user.username.username,
    return_object['api_key'] = apikey,
    return_object['success'] = False

    if apikey is not '':

        # request_user = get_request_user(request)

        if request_user is not anon_lv_model:
            print 'legit user'

            success, time_remaining, valid_till, error, user = auth_api_key(apikey)

            return_object['success'] = success
            if success:
                return_object['valid_till'] = valid_till
                return_object['time_remaining'] = time_remaining
            else:
                return_object['error'] = error

        else:
            print 'user is the anon user'

    else:
        print 'no api key given'

    return HttpResponse(json.dumps(return_object, indent=4), content_type="application/json")


def new_collection(request):
    image = models.Image.objects.get(flickr_id=request.POST['image_id'])
    request_user = get_request_user(request)
    success = True
    users_collections = set()
    users_collections.add('default')

    try:
        name = request.POST.get('collection_name', 'default')
        collection, created = models.ImageCollection.objects.get_or_create(name=name, user=request_user)

        saved_image, created = models.ImageMapping.objects.get_or_create(collection=collection, image=image)

        collection_models = models.ImageCollection.objects.all().filter(user=request_user)
        users_collections = []

        for c in collection_models:
            users_collections.append(c.name)
        users_collections.append('NEW COLLECTION')

    except Exception as e:
        print 'new_collection', str(e), type(e)
        success = False

    query_response = {
        'success': success,
        'collections': list(users_collections)
    }

    return HttpResponse(json.dumps(query_response), content_type="application/json")


def tweet_card(request):
    image = 'http://illustrationarchive.cf.ac.uk/static/media/images/ill-arch-wide.png'
    text = 'Here is a test twitter card'
    title = 'this is the title'
    user = '@Lost_Visions'
    site = 'illustrationarchive.cf.ac.uk'

    return render(request, 'twitter_card.html',
                  {'tweet_image': image,
                   'tweet_text': text,
                   'tweet_title': title,
                   'tweet_site': site,
                   'tweet_user': user},
                  context_instance=RequestContext(request))


def add_images_to_collection(id_list, image_collection, query_response=None, errors=None):
    if query_response is None:
        query_response = {}
    if errors is None:
        errors = []

    added_ids = []
    image_models_to_save = []
    for image_id in id_list:
        try:
            image_model = models.Image.objects.get(flickr_id=image_id)
            added_ids.append(image_id)
            image_models_to_save.append(image_model)
        except Exception as e424253:
            errors.append('Error adding image ' + str(image_id) + ' : ' + str(e424253))

    query_response['ids_added'] = added_ids
    if len(added_ids):
        query_response['success'] = True

        try:
            if not image_collection.pk:
                image_collection.save()
        except Exception as e923:
            errors.append(str(e923))

        for image_model in image_models_to_save:
            try:
                # new_mapping = models.ImageMapping()
                # new_mapping.image = image_model
                # new_mapping.collection = image_collection
                #
                new_mapping = models.ImageMapping.objects.get_or_create(image=image_model, collection=image_collection)
                # new_mapping.save()
            except Exception as e242:
                errors.append('Issue with Mapping ' + str(image_model.flickr_id) + ' : ' + str(e242))
    else:
        errors.append('Added zero images to collection. Collection not saved')
        query_response['success'] = False

    return query_response, errors


@csrf_exempt
def manage_collection(request):
    action = ''
    col_id = ''
    image_collection_name = ''
    api_key = ''
    api_key_user = None
    ids = ''

    if request.method == "POST":
        action = clean(request.POST.get('action', ''))
        col_id = clean(request.POST.get('collection_id', ''))
        image_collection_name = clean(request.POST.get('collection_name', ''))
        api_key = clean(request.POST.get('api_key', ''))
        ids = clean(request.POST.get('image_ids', ''))

    if request.method == "GET":
        action = clean(request.GET.get('action', ''))
        col_id = clean(request.GET.get('collection_id', ''))
        image_collection_name = clean(request.GET.get('collection_name', ''))
        api_key = clean(request.GET.get('api_key', ''))
        ids = clean(request.GET.get('image_ids', ''))

    id_list = ids.split(',')
    id_list = [f_id for f_id in id_list if len(f_id)]

    query_response = {}
    errors = []

    api_key_authd = False
    if len(api_key):
        api_key_authd, time_remaining, valid_till, error, api_key_user = auth_api_key(api_key)
        query_response['api_key_given'] = api_key
        query_response['api_key_authd'] = api_key_authd

        if api_key_authd:
            query_response['api_key_valid_till'] = valid_till
            query_response['api_key_time_remaining'] = time_remaining
        else:
            errors.append(error)

    # print request.user
    # print request.user.is_authenticated()

    if request.user.is_authenticated() or api_key_authd:
        collection_creating_user = None
        if api_key_authd:
            collection_creating_user = api_key_user
        else:
            collection_creating_user = get_request_user(request)

        if action == 'save_new_collection':

            query_response['image_ids_received'] = id_list

            if len(id_list):

                image_collection = models.ImageCollection()
                image_collection.user = collection_creating_user
                image_collection.name = image_collection_name

                if not len(image_collection_name):
                    errors.append('No name given for collection, continuing anyway')
                else:
                    query_response['collection_name_received'] = image_collection_name

                query_response, errors = add_images_to_collection(id_list, image_collection, query_response, errors)

                query_response['collection_id_saved'] = image_collection.id
                # added_ids = []
                # mappings_to_save = []
                # for image_id in id_list:
                #     try:
                #         image_model = models.Image.objects.get(flickr_id=image_id)
                #         new_mapping = models.ImageMapping()
                #         new_mapping.image = image_model
                #
                #         added_ids.append(image_id)
                #         mappings_to_save.append(new_mapping)
                #     except Exception as e424253:
                #         errors.append('Error adding image ' + str(image_id) + ' : ' + str(e424253))
                #
                # query_response['ids_added'] = added_ids
                # if len(added_ids):
                #     query_response['success'] = True
                #
                #     try:
                #         image_collection.save()
                #     except Exception as e923:
                #         errors.append(str(e923))
                #
                #     for mapping in mappings_to_save:
                #         try:
                #             mapping.collection = image_collection
                #             mapping.save()
                #         except Exception as e242:
                #             errors.append(str(e242))
                # else:
                #     errors.append('Added zero images to collection. Collection not saved')
                #     query_response['success'] = False

            else:
                errors.append('No IDs given, will not create empty collection')

        if action == 'add_to_collection':
            query_response['image_ids_received'] = id_list
            query_response['collection_id_received'] = col_id

            image_collection = models.ImageCollection.objects.get(id=col_id)
            if image_collection.user == api_key_user:
                query_response, errors = add_images_to_collection(id_list, image_collection, query_response, errors)
                query_response['collection_id_saved'] = image_collection.id
                query_response['success'] = True
            else:
                query_response['success'] = False
                errors.append('Collection not owned by user with this API key')

        if action == 'delete':
            print 'deleting collection ' + str(col_id)
            image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))
            image_collection.delete()
            query_response['success'] = True

        if action == 'tag_collection':
            tag_word = ''
            wordnet_tag = ''
            tag_info = '[]'
            if request.method == "POST":
                tag_word = clean(request.POST.get('tag', ''))
                wordnet_tag = clean(request.POST.get('tag_synset', ''))
                tag_info = request.POST.get('tag_info', '[]')

            if request.method == "GET":
                tag_word = clean(request.GET.get('tag', ''))
                wordnet_tag = clean(request.GET.get('tag_synset', ''))
                tag_info = request.GET.get('tag_info', '[]')

            tags_xy = ast.literal_eval(tag_info)

            # print pprint.pformat(tags_xy)
            for tag_index in tags_xy:
                user_tag = tags_xy[tag_index]

                tag_word = clean(user_tag.get('tag', ''))
                wordnet_tag = clean(user_tag.get('synset', ''))

                if len(tag_word):
                    # print 'tagging collection ' + str(col_id)
                    image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))

                    image_mappings = models.ImageMapping.objects.filter(collection=image_collection)

                    for image_mapping in image_mappings:

                        try:
                            image_tag = models.Tag()
                            image_tag.tag = tag_word
                            image_tag.image = image_mapping.image
                            image_tag.user = collection_creating_user
                            image_tag.tag_order = clean(user_tag['tag_order'])
                            image_tag.timestamp = parser.parse(str(user_tag['timestamp']))
                            image_tag.save()

                            if len(wordnet_tag):
                                try:
                                    wordnet_tag_model = models.WordnetTag()
                                    wordnet_tag_model.tag = image_tag
                                    wordnet_tag_model.wordnet_synset = wordnet_tag
                                    wordnet_tag_model.save()
                                except Exception as e78624:
                                    print 'e78624' + str(e78624)

                        except Exception as e746224:
                            print 'e746224' + str(e746224)

                    try:
                        collection_tag = models.CollectionTag()
                        collection_tag.tag = tag_word
                        collection_tag.wordnet_synset = wordnet_tag
                        collection_tag.collection = image_collection
                        collection_tag.user = collection_creating_user
                        collection_tag.tag_order = clean(user_tag['tag_order'])
                        collection_tag.timestamp = parser.parse(str(user_tag['timestamp']))
                        collection_tag.save()
                    except Exception as e98723:
                        print 'e98723' + str(e98723)

            query_response['success'] = True

        if action == 'rename':
            # name = request.POST.get('collection_name', '')
            print 'renaming ' + str(col_id) + ' to ' + str(image_collection_name)
            image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))
            image_collection.name = image_collection_name
            image_collection.save()
            query_response['success'] = True

        if action == 'set_image_caption':
            if request.method == "POST":
                image_id = request.POST.get('image_id', '')
                new_caption = request.POST.get('new_caption', '')
            if request.method == "GET":
                image_id = request.GET.get('image_id', '')
                new_caption = request.GET.get('new_caption', '')

            image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))

            image_model = models.Image.objects.get(flickr_id=image_id)
            image_mapping = models.ImageMapping.objects.get(collection=image_collection, image=image_model)

            mapping_caption, created = models.SavedImageCaption.objects.get_or_create(image_mapping=image_mapping)

            mapping_caption.caption = new_caption
            mapping_caption.save()
            query_response['success'] = True

    else:
        query_response['success'] = False

    query_response['errors'] = errors

    return HttpResponse(json.dumps(query_response, indent=4), content_type="application/json")


def get_zip_path(root_folder, book_id, volume='0'):
    book_id = book_id + '_' + volume.lstrip('0')
    # print book_id

    try:
        for a_file in os.listdir(root_folder):
            disk_folder = os.path.join(root_folder, a_file)
            if 'disk5' in disk_folder:
                disk_folder = os.path.join(disk_folder, 'JP2')
            for b_file in os.listdir(disk_folder):
                if book_id in b_file:
                    # print b_file
                    if int(b_file.split('_')[1]) == int(volume):
                        if 'disk5' in disk_folder:
                            return os.path.join(root_folder, os.path.join(os.path.join(a_file, 'JP2'), b_file))
                        else:
                            return os.path.join(root_folder, os.path.join(a_file, b_file))
    except Exception as e:
        print 'get_zip_path', str(e), type(e)

        return None


def find_zip(book_id, volume='0'):
    web_folder = os.path.join('', 'media')
    web_folder = os.path.join(web_folder, 'page_zips')

    root_folder = os.path.join(BASE_DIR, 'lost_visions')
    root_folder = os.path.join(root_folder, 'static')
    root_folder = os.path.join(root_folder, web_folder)
    # zip_path = '/home/ubuntu/PycharmProjects/Lost-Visions/lost_visions/static/media/images/003871282_0_1-324pgs__1023322_dat.zip'

    zip_path = get_zip_path(root_folder, book_id, volume)

    if zip_path is None:
        return None

    archive = zipfile.ZipFile(zip_path, 'r')

    return archive


def find_page(request, book_id, page, volume):

    response = HttpResponse(content_type="image/jpeg")

    archive = find_zip(book_id, volume)
    if archive is None:
        return response

    inner_zipped_file = None
    for zipped_file in archive.namelist():
        page_number_found = zipped_file.split('_')[-1]
        page_number_found = page_number_found.split('.')[0]
        if int(page) == int(page_number_found):
            inner_zipped_file = zipped_file

    if inner_zipped_file is None:
        return response

    # imgdata = archive.read('JP2\\003871282_000015.jp2')
    imgdata = archive.read(inner_zipped_file)


    input_image = StringIO.StringIO(imgdata)
    input_image.seek(0)
    img = Image.open(input_image)

    # save as jpeg instead of jpeg2000. Probable loss of quality
    response['Content-Disposition'] = 'attachment; filename=%s' % str(inner_zipped_file).replace('.jp2', '.jpg')
    img.save(response, "JPEG", quality=80, optimize=True, progressive=True)

    return response


def page_turner(request, book_id, page, volume):
    page_detail = page.split(':')
    page_long = page_detail[0]
    page_short = str(int(page_long))

    # print book_id
    # print page_detail
    # print page_long
    # print page_short
    # print volume



    # print book_id, page, volume
    page_image_data = models.Image.objects.filter(book_identifier=book_id)

    flickr_ids = models.Image.objects.filter(book_identifier=book_id, page=page, volume=volume).values_list('flickr_id', flat=True)
    # print flickr_ids.query
    # print flickr_ids
    flickr_id = ''
    if len(flickr_ids):
        flickr_id = flickr_ids[0]

    title = page_image_data[0].title

    archive = find_zip(book_id, volume)
    pages = []
    if archive is not None:
        for page_name in archive.namelist():
            page_number_found = page_name.split('_')[-1]
            page_number_found = page_number_found.split('.')[0]

            found = False
            for book_image in page_image_data:
                # if book_image.page == page and book_image.volume == volume:
                #     flickr_id = book_image.flickr_id

                if int(book_image.page) == int(page_number_found):
                    found = True
                    pages.append({
                        'page_no': int(page_number_found),
                        'has_image': True,
                        'idx': int(book_image.image_idx)
                    })
                    # only interested in the page if theres > 0
                    # unfortunately idx is useless
                    break
            if not found:
                pages.append({
                    'page_no': int(page_number_found),
                    'has_image': False
                })

    prev = int(page_short) - 1
    next_page = int(page_short) + 1

    render_details = {
        'book_id': book_id,
        'volume': volume,
        'pages': sorted(pages, key=lambda k: k['page_no']),
        'page': page_short,
        'title': title,
        'prev': str(prev).zfill(6),
        'next': str(next_page).zfill(6),
        'split_pre': page_short + ':-1',
        'split_post': page_short + ':+1',
        'flickr_id': flickr_id,
        # 'link': reverse('image', kwargs={'image_id': flickr_id})
    }

    if len(page_detail) > 1:
        pre_post_page = page_detail[1]
        pre_post = ''
        extra_page_number = 0

        if '-1' in pre_post_page:
            extra_page_number = str(int(page_detail[0]) -1)
            pre_post = 'pre'
        if '+1' in pre_post_page:
            extra_page_number = str(int(page_detail[0]) +1)
            pre_post = 'post'

        render_details['pre_post']= pre_post
        render_details['pre_post_number'] = extra_page_number

    render_details['pre_number'] = str(int(page_detail[0]) - 1)
    render_details['post_number'] = str(int(page_detail[0]) + 1)

    return render(request, 'page_turner.html', render_details)

@requires_csrf_token
def software(request):
    return render(request, 'software.html', {})


def exhibition(request, collection_id):

    collection_model = models.ImageCollection.objects.all().get(id=collection_id)
    collection_data = dict()

    mapped_images = models.ImageMapping.objects.filter(collection=collection_model)
    mapped_images_array = []
    for image in mapped_images:
        # print pprint.pformat(image.__dict__)

        image_dict = dict()
        image_dict['flickr_id'] = image.image.flickr_id
        image_dict['title'] = image.image.title
        image_dict['page'] = image.image.page.lstrip('0')
        # image_dict['url'] = image.image.flickr_small_source
        try:
            image_model = get_image_data_with_location([image.image.flickr_id])[0]

            image_info = db_tools.get_image_info(image_model)

            if image_info is None:
                image_info = dict()
            else:
                image_dict['url'] = sanitise_image_info(image_info, request)['imageurl']
        except Exception as e69362:
            print 'get_image_data_with_location', str(e69362), type(e69362)

        try:
            image_mapping_caption = models.SavedImageCaption.objects.get(image_mapping=image)
            image_dict['caption'] = image_mapping_caption.caption
        except Exception as e:
            pass
            # print e

        mapped_images_array.append(image_dict)
        # print pprint.pformat(image_dict)

    collection_data['images'] = mapped_images_array
    collection_data['collection_name'] = collection_model.name

    return_object = {'collection_id': collection_id,
                     'collection_data': collection_data,
                     'collection_creator': get_collection_creator(collection_model),
                     'date': collection_model.timestamp,
                     }
    return render(request, 'exhibition-new.html', return_object)


def book_images(request, image_id):

    book_id = models.Image.objects.filter(flickr_id=image_id).values('book_identifier').distinct()
    book_images = get_book_images(book_id[0]['book_identifier'])
    for book_image in book_images:
        book_image['link'] = reverse('image', kwargs={'image_id': int(book_image['flickr_id'])})
    book_image_count = len(book_images)

    return_data = {
        'book_images': book_images,
        'book_image_count': book_image_count,
    }
    return HttpResponse(json.dumps(return_data, indent=4), content_type="application/json")


def similar_images(request, image_id):
    error = ''
    book_images = []
    powerset_image_data = []
    largest_set = []
    machine_matched_ids = []

    db_count = len(connection.queries)
    img_pick = ImagePicker()
    # book_id = models.Image.objects.filter(flickr_id=image_id).values('book_identifier').distinct()
    # book_id_query_count = len(connection.queries)

    # book_images = get_book_images(book_id[0]['book_identifier'])
    # for book_image in book_images:
    #     book_image['link'] = reverse('image', kwargs={'image_id': int(book_image['flickr_id'])})
    book_image_count = len(book_images)
    # book_images_query_count = len(connection.queries)

    machine_matches = []
    try:
        #TODO optimise
        image_object = models.Image.objects.get(flickr_id=image_id)
        image_object_flickr_id = image_object.flickr_id
        image_matches = models.MachineMatching.objects.filter(Q(metric='CV_COMP_CORREL')) \
                            .filter(Q(image_a=image_object) | Q(image_b=image_object)) \
                            .values_list('image_a__flickr_id', 'image_b__flickr_id') \
                            .order_by('-metric_value')[:20]

        for machine_matched in image_matches:
            if machine_matched[0] == image_object_flickr_id:
                machine_matched_ids.append(machine_matched[1])
            else:
                machine_matched_ids.append(machine_matched[0])

        if len(machine_matched_ids) > 0:
            machine_matches = get_image_data_from_array(machine_matched_ids, request)
    except Exception as e0293:
        print 'machine match error', str(e0293), type(e0293)

    machine_match_query_count = len(connection.queries)
    sorted_id_list = img_pick.get_similar_images_with_tags(image_id)

    similar_image_query_count = len(connection.queries)
    unsorted_image_data = get_image_data_from_array(sorted_id_list, request)
    # unsorted_image_data = get_image_data_with_location(sorted_id_list)

    similar_image_info_query_count = len(connection.queries)

    for similar_id in sorted_id_list:
        image_to_sort = unsorted_image_data[similar_id]
        image_to_sort['link'] = reverse('image', kwargs={'image_id': int(similar_id)})
        largest_set.append(image_to_sort)

    end_query_count = len(connection.queries)

    db_counts = [('db_count', db_count),
                 # ('book_id_query_count', book_id_query_count),
                 # ('book_images_query_count', book_images_query_count),
                 ('machine_match_query_count', machine_match_query_count),
                 ('similar_image_query_count', similar_image_query_count),
                 ('similar_image_info_query_count', similar_image_info_query_count),
                 ('end_query_count', end_query_count)]

    return_data = {'db_counts': db_counts,
                   'similars_id_list': sorted_id_list,
                   'error': error,
                   # 'book_images': book_images,
                   # 'book_image_count': book_image_count,
                   'image_sets': powerset_image_data,
                   'largest_set': largest_set,
                   'largest_set_size': len(largest_set),
                   'machine_matches': machine_matches
                   }
    return HttpResponse(json.dumps(return_data, indent=4), content_type="application/json")


def powerset_generator(i):
    for subset in itertools.chain.from_iterable(itertools.combinations(i, r) for r in range(len(i)+1)):
        yield subset


def get_image_data_dict(image_id):
    image_data_model = models.Image.objects.get(flickr_id=image_id)
    serialized_image_model = serializers.serialize('json', [image_data_model])

    tags = models.Tag.objects.filter(image=image_data_model)
    tags_list = []
    for tag in tags:
        tags_list.append({
            'tag': tag.tag,
            'tag_order': tag.tag_order
        })

    image_location = models.ImageLocation.objects.filter(book_id=image_data_model.book_identifier)
    serialized_location_model = serializers.serialize('json', image_location)

    descriptor_locations = models.DescriptorLocation.objects.filter(image_id=image_data_model)
    serialized_descriptors_model = serializers.serialize('json', descriptor_locations)

    image_matches = models.MachineMatching.objects.filter(Q(image_a=image_data_model) |
                                                          Q(image_b=image_data_model)) \
        .filter(Q(metric='CV_COMP_CORREL')).order_by('-metric_value')
    serialized_matches_model = serializers.serialize('json', image_matches)

    return_data = {
        'bl_flickr_data': json.loads(serialized_image_model),
        'tags': tags_list,
        'descriptors': json.loads(serialized_descriptors_model),
        'image_location': json.loads(serialized_location_model),
        'matches': json.loads(serialized_matches_model)
    }
    return return_data


def image_data(request, image_id):
    return_data = get_image_data_dict(image_id)
    return HttpResponse(json.dumps(return_data, indent=4), content_type="application/json")


def education(request):
    return render(request, 'education.html', {})


def mario_find(request, flickr_id):

    # print flickr_id

    # query = "SELECT wordid, lemma, definition, synsetid, pos, sensenum FROM words LEFT JOIN senses s USING (wordid) " \
    #         "LEFT JOIN synsets USING (synsetid) where lemma like %s " \
    #         "order by length(lemma), sensenum COLLATE NOCASE ASC limit %s"

    results = mario_models.Profiles.objects.filter(fileid__contains=flickr_id)

    # .objects.db_manager('wordnet').raw(query, [searchword + '%', limit])


    # found_ids = models.Profiles()

    stuff = {}

    if len(results) > 0:
        for result in results:
            # print pprint.pformat(result.__dict__)

            # normalised = mario_models.Normalized.objects.filter(profileid=result.id)
            normalised = mario_models.Normalized.objects.filter(profileid=result)

            # print normalised.query

            stuff[result.pk] = json.loads(serializers.serialize('json', normalised))

            tags_2_profiles =  result.tag2profile_set.all()

            # print tags_2_profiles
            stuff['tags'] = []

            for tag_relation in tags_2_profiles:
                for tag in mario_models.Tags.objects.filter(tagid=tag_relation.tagid):
                    stuff['tags'].append(tag.tag)

                    # tag2profile_ids = mario_models.Tag2Profile.objects.filter(profileid=result)
                    #
                    # print tag2profile_ids.__dict__
                    #
                    # for tag_id in tag2profile_ids:
                    #     print tag_id
                    #     tag = mario_models.Tags.objects.filter(tagid=tag_id.tagid)
                    #
                    #     stuff['tags'].append(tag)

    # return_data = serializers.serialize('json', results)
    return HttpResponse(json.dumps(stuff, indent=4), content_type="application/json")


def help(request):
    return render(request, 'help.html', {}, context_instance=RequestContext(request))

@requires_csrf_token
def request_public_exhibition(request):
    if request.user.is_authenticated():

        # print request.POST

        collection_name = request.POST.get('collection_name', '*UNKNOWN*')
        collection_id = request.POST.get('collection_id', '*UNKNOWN*')

        email_text = 'To Lost Visions/ Illustration Archive Administrator\n\n'
        email_text += 'User ' + get_request_user(request).username.username + \
                      ' has requested that a collection named *' + collection_name + \
                      '* with collection ID *' + collection_id + '* be made into a Public Exhibition.\n\n'
        email_text += 'Click <here> to accept.\n\n'
        email_text += 'Thanks.\n\nThis is an automated message, please do not reply.'
        email_text += '\n\nLost Visions/ Illustration Archive, 2015'

        html_text = '<strong>To Lost Visions/ Illustration Archive Administrator</strong><br><br>'
        html_text += '<p>User ' + get_request_user(request).username.username + \
                     ' has requested that a collection named *' + collection_name + \
                     '* with collection ID *' + collection_id + '* be made into a Public Exhibition.</p><br>'
        html_text += '<p>Click <a href="illustrationarchive.cf.ac.uk' + reverse('exhibition', kwargs={'collection_id': collection_id}) + \
                     '">Here</a> to review it.</p><br>'
        html_text += '<p>Click <a href="illustrationarchive.cf.ac.uk' + reverse('accept_public_exhibition', kwargs={'collection_id': collection_id}) + \
                     '">Here</a> to accept.</p><br>'
        html_text += '<p>Thanks.</p><p>This is an automated message, please do not reply.</p>'
        html_text += '<br><p>Lost Visions/ Illustration Archive, 2015<p>'

        email = EmailMultiAlternatives('Request for Public Exhibition ' + collection_name + ' ' + collection_id,
                                       email_text, to=ADMIN_EMAIL_ADDRESSES)
        email.attach_alternative(html_text, "text/html")
        res = email.send()

        return HttpResponse(json.dumps({'success': res}, indent=4), content_type="application/json")


def accept_public_exhibition(request, collection_id):
    if request.user.is_authenticated():
        if get_request_user(request).username.username == 'davejones':
            msg = 'OK added ' + str(collection_id)

            # This needs explanation
            #             We're going to copy/ clone the users existing collection and give this clone to the admin user

            # Get the admin user by name
            # TODO dont use name, thats stupid
            admin_user = models.User.objects.get(username='davejones')
            admin_user = models.LostVisionUser.objects.get(username=admin_user)

            # Get the user collection we're going to clone
            old_collection_model = models.ImageCollection.objects.get(id=collection_id)

            # Create a new Image collection with the admin user as the owner
            # Give it the same name as the original
            new_collection_model = models.ImageCollection()

            new_collection_name = old_collection_model.name + \
                                  '. Created by ' + old_collection_model.user.username.username
            new_collection_model.name = new_collection_name
            new_collection_model.user = admin_user
            new_collection_model.save()

            # Create all new Image mappings the same as the previous ones
            # add them to the new collection
            image_mappings = models.ImageMapping.objects.filter(collection=old_collection_model)
            for old_mapping in image_mappings:

                new_mapping = models.ImageMapping()
                new_mapping.image = old_mapping.image
                new_mapping.collection = new_collection_model
                new_mapping.save()

                # Take all the captions from the previous collection too
                # save them to the new mapping for each image
                old_mapping_captions = models.SavedImageCaption.objects.filter(image_mapping=old_mapping)
                for old_caption in old_mapping_captions:
                    new_caption = models.SavedImageCaption()
                    new_caption.caption = old_caption.caption
                    new_caption.image_mapping = new_mapping
                    new_caption.save()

            # Create a publicExhibition object with the new collection
            # Store a reference to the previous collection the user created
            # save it
            new_public_exhibition = models.PublicExhibition()
            new_public_exhibition.collection = new_collection_model
            new_public_exhibition.user_collection = old_collection_model
            new_public_exhibition.save()

        else:
            msg = 'not davejones'
    else:
        msg = 'Not authed'
    return render(request, 'accept_public_exhibition.html', {'msg': msg}, context_instance=RequestContext(request))


def public_exhibition_specific(request, exhibition_id):
    exhibition_model = models.PublicExhibition.objects.all().filter(visible=True).get(id=exhibition_id)
    return get_public_exhibition_data(request, exhibition_model)


def latest_public_exhibition(request):
    exhibition_models = models.PublicExhibition.objects.all().filter(visible=True).order_by('-timestamp')
    recent_exhibition_model = exhibition_models[0]
    return get_public_exhibition_data(request, recent_exhibition_model)


def get_public_exhibition_data(request, exhibition_model):

    collection_model = exhibition_model.collection
    collection_data = dict()

    mapped_images = models.ImageMapping.objects.filter(collection=collection_model)
    mapped_images_array = []

    for image in mapped_images:
        # print pprint.pformat(image.__dict__)

        image_dict = dict()
        image_dict['flickr_id'] = image.image.flickr_id
        image_dict['title'] = image.image.title
        image_dict['page'] = image.image.page.lstrip('0')
        # image_dict['url'] = image.image.flickr_small_source
        try:
            image_model = get_image_data_with_location([image.image.flickr_id])[0]
            image_info = db_tools.get_image_info(image_model)
            if image_info is None:
                image_info = dict()
            else:
                image_dict['url'] = sanitise_image_info(image_info, request)['imageurl']

        except Exception as e69362:
            pass
            # print 'e69362' + str(e69362)

        try:
            image_mapping_caption = models.SavedImageCaption.objects.get(image_mapping=image)
            image_dict['caption'] = image_mapping_caption.caption
        except Exception as e:
            pass
            # print e

        mapped_images_array.append(image_dict)
        # print pprint.pformat(image_dict)

    collection_data['images'] = mapped_images_array
    collection_data['collection_name'] = collection_model.name

    return_object = {'collection_id': collection_model.id,
                     'collection_data': collection_data,
                     'date': exhibition_model.timestamp,
                     'collection_creator': get_collection_creator(collection_model)}
    return render(request, 'public_exhibition.html', return_object, context_instance=RequestContext(request))


def random_search(request):

    results = dict()
    results['advanced'] = dict()

    number_of_results_int = 200

    number_of_images = models.Image.objects.count()
    rand_image_pk = randint(1, number_of_images)
    random_array = sample(range(0, number_of_images), number_of_results_int)


    ors = []
    for id in random_array:
        ors.append(Q(id=id))

    all_results = models.Image.objects.filter(reduce(operator.or_, ors)).values_list('flickr_id', flat=True)

    to_join = []
    for result in all_results:
        to_join.append(result)

    all_image_ids = ','.join(to_join)
    total_results = len(all_results)

    results['advanced'] = []

    response_data = {'results': results, 'size': total_results}

    user_collections = []
    if request.user.is_authenticated():
        collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
        for model in collection_models:
            user_collections.append({'name': model.name,
                                     'id': str(model.id)})

    return render(request, 'random_search_results.html',
                  {'results': response_data,
                   'query_array': request.GET,
                   'all_image_ids': all_image_ids,
                   'number_to_show': 30,
                   'user_collections': user_collections},
                  context_instance=RequestContext(request))


def public_exhibition_list(request):

    response_data = []

    exhibition_models = models.PublicExhibition.objects.all().filter(visible=True).order_by('-timestamp')

    for ex in exhibition_models:
        image_info = get_images_for_flickr_id(int(ex.collection.imagemapping_set.all()[0].image.flickr_id))

        response_data.append({
            'timestamp': str(ex.timestamp.strftime('%Y-%m-%d')),
            'id': ex.id,
            'name': ex.collection.name,
            'collection_id': ex.collection.id,
            'img_info': image_info[0]
        })

    trusted_ids = settings.TRUSTED_COLLECTIONS

    ors = [Q(id=x) for x in trusted_ids]
    # ors.append(Q(id=an_id))

    collection_models = models.ImageCollection.objects.all()
    collection_models = collection_models.filter(reduce(operator.or_, ors))

    trusted_collections = []

    for collection_model in collection_models:
        image_mapping_set = collection_model.imagemapping_set.all()
        if image_mapping_set.count() > 0:

            image_datas = get_image_data_from_array([image_mapping_set[0].image.flickr_id], request)
            image_url = ''
            for img_data_id, img_data in image_datas.items():
                image_url = img_data['img_small']

            trusted_collections.append({
                'collection_name': collection_model.name,
                'collection_size': collection_model.imagemapping_set.all().count(),
                'collection_id': collection_model.id,
                'collection_creator': get_collection_creator(collection_model),
                'collection_timestamp': collection_model.timestamp.strftime('%Y-%m-%d'),
                'image_url': image_url
            })

    return render(request, 'public_exhibition_list.html', {
        'results': response_data,
        'trusted_collections': trusted_collections
    }, context_instance=RequestContext(request))


def view_collection(request, collection_id, page):

    # collection_model = models.ImageCollection.objects.get(id=collection_id, user=get_request_user(request))

    collection_model = models.ImageCollection.objects.get(id=collection_id)
    results = {}
    mapped_images = collection_model.imagemapping_set.all()

    # mapped_images = models.ImageMapping.objects.filter(collection=collection_model)
    mapped_images_full_count = mapped_images.count()

    images_per_page = 50
    total_number_of_pages = (mapped_images_full_count // images_per_page) + 1

    page = int(page)
    if page < 1:
        page = 1
    if page > total_number_of_pages:
        page = total_number_of_pages

    images_start = (page-1) * images_per_page
    images_end = page * images_per_page

    image_ids = []
    for image_map in mapped_images[images_start: images_end]:
        image_ids.append(image_map.image.flickr_id)

    all_image_ids = ','.join(image_ids)

    results['advanced'] = []

    mode = 'not_logged_in'

    if not request.user.is_authenticated():
        mode = 'not_logged_in'
    else:
        if collection_model.user == get_request_user(request):
            mode = 'owner'
        else:
            mode = 'logged_in_not_owner'

    # dots = False
    # if total_number_of_pages < 6:
    #     pages = range(1, total_number_of_pages + 1)
    # else:

    dots = True
    # if page <= 5:
    #     pages = range(2, 6)
    # else:
    range_max = page + 4
    if range_max > total_number_of_pages:
        range_max = total_number_of_pages
    range_min = page - 4
    if range_min < 2:
        range_min = 2

    # print range_min, page, range_max

    pages = range(range_min, range_max)

    response_data = {'results': results,
                     'pages': pages,
                     'page_multiplier': get_page_multipliers(total_number_of_pages, page),
                     'dots': dots,
                     'this_page': page,
                     'total_pages': total_number_of_pages,
                     'size': mapped_images_full_count}

    user_collections = []
    if request.user.is_authenticated():
        collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
        for model in collection_models:
            user_collections.append({'name': model.name,
                                     'id': str(model.id)})
        user_collections.append({'name': 'NEW COLLECTION',
                                 'id': 0})

    collection_tags = models.CollectionTag.objects.filter(collection=collection_model).values_list('tag', flat=True).distinct()

    # print pprint.pformat(response_data)

    return render(request, 'view_collection.html', {
        'results': response_data,
        'user_collections': user_collections,
        'mode': mode,
        'query_array': request.GET,
        'all_image_ids': all_image_ids,
        'number_to_show': 30,
        'collection_name': collection_model.name,
        'collection_tags': collection_tags,
        'collection_id': collection_model.id,
        'collection_creator': get_collection_creator(collection_model)
    }, context_instance=RequestContext(request))


# A bit anglo-saxon specific i18n in future
def get_collection_creator(collection_model):
    collection_creator = str(collection_model.user.username.username)
    first_name = collection_model.user.username.first_name
    second_name = collection_model.user.username.last_name
    if len(first_name) or len(second_name):
        try:
            capitalized_collection_creator = str(first_name.capitalize() + ' ' + second_name.capitalize())
            return capitalized_collection_creator
        except:
            return collection_creator
    return collection_creator


def download_collection_ready(request):
    collection_id = 1
    return render(request, 'download_collection_ready.html',
                  {'collection_id': collection_id},
                  context_instance=RequestContext(request))


def zip_available(request, collection_id):

    url = '/file/file.txt'

    return HttpResponse(json.dumps({'success': False,
                                    'url': static(url)
                                    }, indent=4), content_type="application/json")


def research(request):
    return render_to_response('research.html')


all_id_list = []
fname = 'lost_visions/scrape/all_id_file.txt'
if os.path.isfile(fname):
    with open(fname, 'r') as all_id_file:
        all_ids = all_id_file.read()
        all_id_list = ast.literal_eval(all_ids)


def get_thumb_url(next_id):
    image_data_text = requests.get('http://lost-visions.cf.ac.uk/image_data/{}'.format(next_id))
    # image_data = json.loads(image_data_text.text)
    image_data = image_data_text.json()
    # print image_data

    volume = image_data['bl_flickr_data'][0]['fields']['volume']
    page = image_data['bl_flickr_data'][0]['fields']['page']

    for a in image_data['image_location']:
        if a['fields']['page'] == page:
            if a['fields']['volume'] == volume:

                next_url = a['fields']['location']

                if int(image_data['bl_flickr_data'][0]['fields']['date']) < 1898:
                    next_url = next_url.replace(
                        '/scratch/lost-visions/images-found/',
                        # '/static/media/found/'
                        '/static/media/images/resized/'

                    )
                    next_url = next_url.replace(
                        'jpg', 'jpg.thumb.jpg'

                    )
                else:
                    next_url = next_url.replace(
                        '/scratch/lost-visions/images-found/',
                        '/static/media/found/'
                    )
                # next_url = next_url.replace(
                #     '[', '%5B'
                # )
                next_url = 'http://lost-visions.cf.ac.uk{}'.format(next_url)
                return next_url


def image_sorter(request):

    print request.GET
    category = 'Britain Outline'

    prev_user_opinion = request.GET.get('user_opinion')
    prev_image_id = request.GET.get('image_id')

    if prev_user_opinion == '1':
        with open('lost_visions/scrape/{}.txt'.format(category), 'a') as yes_file:
            yes_file.write('{}\n'.format(prev_image_id))
    elif prev_user_opinion == '-1':
        with open('lost_visions/scrape/not_{}.txt'.format(category), 'a') as no_file:
            no_file.write('{}\n'.format(prev_image_id))
    else:
        with open('lost_visions/scrape/no_opinion_{}.txt'.format(category), 'a') as none_file:
            none_file.write('{}\n'.format(prev_image_id))

    itr = request.GET.get('itr', -1)
    itr = int(itr) + 1
    next_id = all_id_list[itr]
    print next_id

    next_url = get_thumb_url(next_id)

    percent = (float(itr) / len(all_id_list)) * 100

    return render(request, 'image_sorter.html',
                  {
                      'user_opinion': prev_user_opinion,
                      'itr': itr,
                      'image_id': next_id,
                      'next_url': next_url,
                      'category': category,
                      'percent': percent,
                      'total': len(all_id_list)
                  },
                  context_instance=RequestContext(request))
