import ast
import json
import os
from random import randint
import re
import urllib
import urllib2
import zipfile
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import StringIO
from PIL import Image
from dateutil import parser
from dateutil.tz import tzlocal
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect


# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
import operator
from pygeoip import GeoIP
from crowdsource.settings import BASE_DIR, STATIC_ROOT, STATIC_URL
from lost_visions import forms, models
# from lost_visions.models import Tag, GeoTag, SearchQuery, User, LostVisionUser, Image, ImageText
from ipware.ip import get_ip
from bleach import clean
from lost_visions.categories import CategoryManager

from lost_visions.utils import db_tools
from lost_visions.utils.db_tools import get_next_image_id, read_tsv_file
from lost_visions.utils.flickr import getImageTags

@requires_csrf_token
def home(request):
    # print request.user
    # if request.user.username:
    #     print request.user.username
    return render(request, 'home.html',
                  context_instance=RequestContext(request))


@requires_csrf_token
def image_tags(request):
    print request.get_full_path()

    if request.method == 'POST':
        print request.POST
        print request.user

        image = models.Image.objects.get(flickr_id=request.POST['image_id'])
        request_user = get_request_user(request)

        image_text = models.ImageText()
        image_text.caption = clean(request.POST.get('input_caption', ''), strip=True)
        image_text.description = clean(request.POST['image_description'], strip=True)
        image_text.image = image
        image_text.user = request_user

        if image_text.description == '' and image_text.caption == '':
            print 'not worth saving blank image text'
        else:
            image_text.save()

        if request.POST['tag_info'] and len(request.POST['tag_info'].decode('utf-8')) > 0:
            tag_info = request.POST['tag_info']
            tags_xy = ast.literal_eval(tag_info)

            for user_tag in tags_xy:
                try:
                    alternative_words = db_tools.list_wordnet_links(user_tag['synset'])[::-1]
                    alternative_words.append([user_tag['tag'], [0, 0]])

                    for index, weighted_word in enumerate(alternative_words):
                        tag = models.Tag()
                        word = weighted_word[0]
                        print word
                        tag.tag = clean(word, strip=True)
                        tag.x_percent = clean(str(user_tag['x_percent']), strip=True)
                        tag.y_percent = clean(str(user_tag['y_percent']), strip=True)
                        # try:
                        # date_object = datetime.strptime(str(user_tag['datetime']), '%Y-%m-%dT%H:%M:%S.%f')
                        date_object = parser.parse(str(user_tag['datetime']))
                        tag.timestamp = date_object
                        # except Exception as e3:
                        #     print e3
                        #     pass

                        tag_order = str((int(clean(str(user_tag['tag_order']), strip=True)) + 1) * 100)

                        print tag_order

                        tag_hyp_dist = int(weighted_word[1][0]) + 1
                        tag_syn_val = int(weighted_word[1][1]) + 1
                        tag_order += str(tag_hyp_dist * 100) + str(tag_syn_val * 100)

                        print tag_order
                        tag.tag_order = tag_order

                        if image and request_user:
                            tag.image = image
                            tag.user = request_user
                        tag.save()
                except:
                    pass

        image.views_completed += 1
        image.save()

    return random_image(request)


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
    # todo redirect
    return redirect('image', image_id=image_id)
    # return image(request, image_id)


def is_user_tag(tag):
    # returns True if the tag is not
    # a British Library auto tag

    lowered = tag.lower()
    bl_tags = ["small", "medium", "large", "public_domain", "mechanical_curator", "bldigital"]

    if lowered in bl_tags:
        return False
    else:
        return True



@requires_csrf_token
def image(request, image_id):
    print image_id

    image_id = clean(image_id, strip=True)

    image_info = db_tools.get_image_info(image_id)

    if image_info is None:
        image_url_part = image_id
        image_info = dict()
    else:
        print image_info['imageurl']
        image_url_part = (image_info['imageurl'].rsplit('/', 1)[1]).split('_')[0]

    formatted_info = dict()

    # try:
    #     #cut image ID from image URL
    #     #get Flickr tags for this image
    #     flickr_tags = getImageTags('http://www.flickr.com/photos/britishlibrary/' + image_url_part, size='z')
    #     author = ""
    #     if 'Author' in flickr_tags:
    #         print "found author : " + flickr_tags['Author']
    #         author = flickr_tags['Author']
    #
    #     if not 'imageurl' in image_info and 'image_location' in flickr_tags:
    #         image_info['imageurl'] = flickr_tags['image_location']
    #
    #     tags = {}
    #     for tag in flickr_tags:
    #         if is_number(tag) and is_user_tag(flickr_tags[tag]):
    #             if flickr_tags[tag].lower() != author.lower():
    #                 try:
    #                     # TODO utf fix
    #                     print "*" + str(flickr_tags[tag]).lower() + "* *" + str(author).lower() + "*"
    #                 except:
    #                     pass
    #
    #                 tags[tag] = flickr_tags[tag]
    #         else:
    #             image_info[tag] = flickr_tags[tag].replace('&quot;', '"')
    #
    #
    #     formatted_info['Issuance'] = image_info.get('Issuance', "")
    #     formatted_info['Date of Publishing'] = image_info.get('Date of Publishing', "")
    #     formatted_info['Title'] = image_info.get('Title', "")
    #     formatted_info['Volume'] = image_info.get('vol', "")
    #     formatted_info['Author'] = image_info.get('Author', "")
    #     formatted_info['Book ID'] = image_info.get('imagesfrombook', "")
    #     formatted_info['Place of Publishing'] = image_info.get('Place of Publishing', "")
    #     formatted_info['Shelfmark'] = image_info.get('Shelfmark', "")
    #     formatted_info['Page'] = image_info.get('Page', "")
    #     formatted_info['Identifier'] = image_id
    #
    # except Exception as e:
    #     print 'flickr access error : ' + str(e)

    formatted_info['Issuance'] = image_info.get('Issuance', "")
    formatted_info['Date of Publishing'] = image_info.get('date', "")
    formatted_info['Title'] = image_info.get('title', "")
    formatted_info['Volume'] = image_info.get('volume', "")
    formatted_info['Author'] = image_info.get('first_author', "")
    formatted_info['Book ID'] = image_info.get('book_identifier', "")
    formatted_info['Place of Publishing'] = image_info.get('pubplace', "")
    formatted_info['Shelfmark'] = image_info.get('BL_DLS_ID', "")
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

    print image_info

    tags_for_image = models.Tag.objects.all().filter(image__flickr_id=image_id).values('tag') \
        .annotate(uses=Count('tag'))

    collection_models = models.ImageCollection.objects.all().filter(user=get_request_user(request))
    users_collections = set()
    users_collections.add('default')
    for c in collection_models:
        users_collections.add(str(c.name))
    users_collections.add('NEW COLLECTION')

    return render(request, 'image.html',
                  {'image': image_info,
                   'book_id': image_info.get('book_identifier', ""),
                   'volume': image_info.get('volume', ""),
                   'page': image_info.get('page', ""),
                   'formatted_info': formatted_info,
                   'image_id': image_id,
                   'image_tags': json.dumps(list(tags_for_image)),
                   # 'category_data': category_data,
                   'user_collections': list(users_collections),
                   'linked_images': linked_image_data,
                   'this_url': reverse('image', kwargs={'image_id': image_id})},
                  context_instance=RequestContext(request))


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
    print request.POST
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

    print request.POST
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

    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
    print 'map for image : ' + image_id

    y = 51.49006473014369
    x = -3.1805146484375
    swy = 50.49006473014369
    swx = -4.1805146484375
    ney = 52.49006473014369
    nex = -2.1805146484375

    print request.GET

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


@requires_csrf_token
def coords(request, image_id):

    # print image_id
    print request.POST

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
        print e

    # return render(request,
    #               'image_map.html',
    #               {'image_id': image_id,
    #                'image_coords_msg': 'Thank you. You may save another region, or close this window'},
    #               context_instance=RequestContext(request))
    return map(request, image_id)

@requires_csrf_token
def save_image(request):
    if request.is_ajax():
        if request.POST.get('delete_image', False):
            try:
                # TODO this can go soon
                delete_image = models.SavedImages.objects.get(image__flickr_id=request.POST['image_id'])
                delete_image.delete()
            except Exception as e:
                print e

            try:
                # TODO use this from now on
                c_id = request.POST['collection_id']
                collection = models.ImageCollection.objects.get(id=c_id, user=get_request_user(request))

                saved_image = models.ImageMapping.objects.get(collection=collection, image__flickr_id=request.POST['image_id'])
                saved_image.delete()
            except Exception as e:
                print e

            return HttpResponse('Removed Image ' + request.POST['image_id'])
        else:
            try:
                user = get_request_user(request)
                image = models.Image.objects.get(flickr_id=request.POST['image_id'])

                if user and image and user.username.username is not 'Anon_y_mouse':
                    image_to_save = models.SavedImages.objects.get_or_create(user=user, image=image)
                    # image_to_save.user = user
                    # image_to_save.image = image
                    #
                    # image_to_save.save()

                    return HttpResponse('Saved Image ' + request.POST['image_id'])
            except Exception as e:
                print e
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
            for image in mapped_images:
                image_dict = dict()
                image_dict['flickr_id'] = image.image.flickr_id
                image_dict['title'] = image.image.title
                image_dict['page'] = image.image.page.lstrip('0')
                image_dict['url'] = image.image.flickr_small_source

                mapped_images_array.append(image_dict)

            collection_data['images'] = mapped_images_array
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


def image_category(request):
    print request.POST
    cat_id = request.POST.get('category_id', '-1')

    try:
        image_id = request.POST.get('image_id', None)
        if image_id is not None:
            category_manager.update_image_actions(image_id)
            category_name = category_manager.get_tag_for_category_id(cat_id)
            if category_name is not None:
                tag = models.Tag()
                tag.tag = category_name
                tag.image = models.Image.objects.get(flickr_id=request.POST['image_id'])
                tag.user = get_request_user(request)
                tag.timestamp = datetime.now(tzlocal())
                tag.tag_order = 0
                tag.save()
    except Exception as e:
        print e
        pass

    category_data = category_manager.get_category_data(cat_id)

    return HttpResponse(json.dumps(category_data), content_type="application/json")


def search_advanced(request):
    return render(request, 'search_advanced.html', {}, context_instance=RequestContext(request))


def do_advanced_search(request):
    print request.GET

    keywords = request.GET.get('keyword', '')
    keywords = keywords.replace(' ', '+')

    year = request.GET.get('year', '')
    author = request.GET.get('author', '')
    illustrator = request.GET.get('illustrator', '')
    number_of_results = request.GET.get('num_results', '')
    book_id = request.GET.get('book_id', '')
    publisher = request.GET.get('publisher', '')
    publishing_place = request.GET.get('publishing_place', '')
    title = request.GET.get('title', '')

    results = dict()
    results['advanced'] = dict()
    total_results = 0

    all_results = models.Image.objects.all()

    readable_query = 'Images '
    all_image_ids = ''
    filtered = False

    if len(keywords):
        q_or_objects = []

        for subword in keywords.split('+'):

            for keyword_image_flickr_id in models.Tag.objects \
                    .filter(tag__icontains=subword).values_list('image__flickr_id', flat=True).distinct():
                if keyword_image_flickr_id:
                    q_or_objects.append(Q(flickr_id=keyword_image_flickr_id))

            for keyword_image_flickr_id in models.ImageText.objects \
                    .filter( Q(caption__icontains=subword ) | Q( description__icontains=subword)) \
                    .values_list('image__flickr_id', flat=True).distinct():
                if keyword_image_flickr_id:
                    q_or_objects.append(Q(flickr_id=keyword_image_flickr_id))

                    # q_or_objects.append(Q(title__icontains=keywords))


        if len(q_or_objects) > 0:
            all_results = all_results.filter(reduce(operator.or_, q_or_objects))
            filtered = True

        readable_query += ' with keyword(s) ' + keywords

    if len(year):
        decade = year[0:3]
        all_results = all_results.filter((Q(date__startswith=decade)))
        filtered = True
        readable_query += ' for the ' + year + "'s"

    if len(author):
        # print author
        all_results = all_results.filter(Q(first_author__icontains=author))
        filtered = True
        readable_query += ' with author ' + author

    if len(title):
        all_results = all_results.filter(Q(title__icontains=title))
        filtered = True
        readable_query += ' with title ' + title

    if len(illustrator):
        q_or_objects = []
        for illustrator_book_id in models.BookIllustrator.objects \
                .filter(name__icontains=illustrator).values_list('book_id', flat=True).distinct():
            if illustrator_book_id:
                q_or_objects.append(Q(book_identifier=str(illustrator_book_id)))

        if len(q_or_objects) > 0:
            all_results = all_results.filter(reduce(operator.or_, q_or_objects))
            filtered = True
            readable_query += ' with illustrator ' + illustrator

    if len(book_id):
        all_results = all_results.filter(book_identifier=book_id)
        filtered = True
        title = models.Image.objects.values_list('title', flat=True).filter(book_identifier=book_id)[:1].get()
        readable_query += ' for book title ' + title

    if len(publisher):
        all_results = all_results.filter(Q(publisher__icontains=publisher))
        filtered = True
        readable_query += ' from publisher ' + publisher

    if len(publishing_place):
        all_results = all_results.filter(Q(pubplace__icontains=publishing_place))
        filtered = True
        readable_query += ' published in ' + publishing_place


    number_of_results_int = 50
    if number_of_results is not '':
        try:
            number_of_results_int = int(number_of_results)
        except:
            pass
    readable_query += '. Showing first ' + str(number_of_results_int) + ' results. '

    all_results = all_results.values_list('flickr_id', flat=True).distinct()
    # print all_results.query

    if all_results.count() < 5000:
        for result in all_results:
            total_results += 1
            all_image_ids += result + ','
        readable_query += '(' + str(len(all_results)) + ' found)'
    else:
        if not filtered:
            readable_query = 'No search filters applied, please add more detail to the query'
        else:
            readable_query += 'Please add more detail to the query. '

            for result in all_results[:5000]:
                total_results += 1
                all_image_ids += result + ','
            readable_query += 'Only returning first 5000 images of (' + str(len(all_results)) + ' found)'

    results['advanced'] = []

    response_data = {'results': results, 'size': total_results, 'search_string': keywords}

    return render(request, 'advanced_search_results.html',
                  {'results': response_data,
                   'query': readable_query,
                   'all_image_ids': all_image_ids,
                   'number_to_show': number_of_results_int},
                  context_instance=RequestContext(request))


def data_autocomplete(request):
    print request.GET

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


def get_image_data(request):

    # print request.POST

    ids = request.POST.get('image_ids', '')
    tag_results_dict = dict()

    if ids:
        id_list = ids.split(',')

        # print id_list

        q_or_objects = []
        for image_id in id_list:
            if image_id:
                q_or_objects.append(Q(flickr_id=image_id))

        if len(q_or_objects) > 0:
            image_data = models.Image.objects.filter(reduce(operator.or_, q_or_objects))

            # print image_data

            for result in image_data:
                try:
                    tag_result = dict()
                    tag_result['title'] = result.title
                    tag_result['img'] = result.flickr_small_source
                    # tag_result['img'] = db_tools.get_image_info(result.flickr_id)['imageurl']
                    tag_result['date'] = result.date
                    tag_result['page'] = result.page.lstrip('0')
                    tag_result['book_id'] = result.book_identifier
                    tag_result['author'] = result.first_author
                    tag_result['link'] = reverse('image', kwargs={'image_id': int(result.flickr_id)})

                    tag_results_dict[result.flickr_id] = tag_result
                except Exception as e:
                    # print 'err'
                    # print result
                    pass
                    # print tag_results_dict

    return HttpResponse(json.dumps(tag_results_dict), content_type="application/json")


def user_dl_all(request):
    print request.GET

    collection_ids = request.GET.get('collection_ids')

    print collection_ids
    if collection_ids:
        # collection_list = ast.literal_eval(collection_ids)
        collection_list = collection_ids.split(',')

        filenames = dict()
        for image_id in collection_list:
            image_info = db_tools.get_image_info(image_id)

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
                fpath = 'http://lost-visions.cf.ac.uk' + fpath
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


def stats(request):

    tags_for_image = models.Tag.objects.all().values('tag').annotate(uses=Count('tag'))
    u = 1
    most_used_tag = ''
    for v in list(tags_for_image):
        if v['uses'] > u:
            u = v['uses']
            most_used_tag = v['tag']

    metrics = dict()
    metrics['total_tags_number'] = models.Tag.objects.count()
    metrics['total_tagged_image_number'] = models.Tag.objects.values('image__id').distinct().count()

    return render(request, 'stats.html',
                  {
                      'metrics': metrics,
                      'image_tags': json.dumps(list(tags_for_image)),
                      'most_used_tag_count': u,
                      'most_used_tag' : most_used_tag
                  },
                  context_instance=RequestContext(request))


def haystack_search(request):
    query_response = {'hello': 'world', 'test': ['a', 'b', 3]}

    return HttpResponse(json.dumps(query_response), content_type="application/json")


def download_collection(request):
    collection_id = request.GET.get('collection_id')

    image_collection = models.ImageCollection.objects.all().get(id=collection_id)

    images = models.ImageMapping.objects.filter(collection=image_collection)

    image_ids = []
    for image_mapping in images:
        image_ids.append(image_mapping.image.flickr_id)

    filenames = dict()
    for image_id in image_ids:
        image_info = db_tools.get_image_info(image_id)

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
    zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)

    for image_id in filenames:

        fpath = filenames[image_id].replace(' ', '%20')

        filename = os.path.join('/tmp/', image_id + '.jpg')
        if 'static/media' in fpath:
            fpath = 'http://lost-visions.cf.ac.uk' + fpath
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
    # return redirect('user_profile_home')


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
        print e
        success = False

    query_response = {
        'success': success,
        'collections': list(users_collections)
    }

    return HttpResponse(json.dumps(query_response), content_type="application/json")


def tweet_card(request):
    image = 'http://lost-visions.cf.ac.uk/static/media/images/ill-arch-wide.png'
    text = 'Here is a test twitter card'
    title = 'this is the title'
    user = '@Lost_Visions'
    site = 'lost-visions.cf.ac.uk'

    return render(request, 'twitter_card.html',
                  {'tweet_image': image,
                   'tweet_text': text,
                   'tweet_title': title,
                   'tweet_site': site,
                   'tweet_user': user},
                  context_instance=RequestContext(request))


def manage_collection(request):
    if request.user.is_authenticated():
        action = request.POST.get('action', '')
        col_id = request.POST.get('collection_id', '')
        if action == 'delete':
            print 'deleting collection ' + str(col_id)
            image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))
            image_collection.delete()

        if action == 'rename':
            name = request.POST.get('collection_name', '')
            print 'renaming ' + str(col_id) + ' to ' + str(name)
            image_collection = models.ImageCollection.objects.all().get(id=col_id, user=get_request_user(request))
            image_collection.name = name
            image_collection.save()

    query_response = {
        'success': True,
        }
    return HttpResponse(json.dumps(query_response), content_type="application/json")


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
        print e

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

    print book_id
    print page_detail
    print page_long
    print page_short
    print volume

    image_data = models.Image.objects.filter(book_identifier=book_id)
    title = image_data[0].title

    archive = find_zip(book_id, volume)
    pages = []
    if archive is not None:
        for page_name in archive.namelist():
            page_number_found = page_name.split('_')[-1]
            page_number_found = page_number_found.split('.')[0]

            found = False
            for book_image in image_data:
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
        'split_post': page_short + ':+1'
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

    return render(request, 'page_turner.html', render_details)


def software(request):
    return render_to_response('software.html')


def exhibition(request, collection_id):

    collection_model = models.ImageCollection.objects.all().get(id=collection_id)
    collection_data = dict()

    mapped_images = models.ImageMapping.objects.filter(collection=collection_model)
    mapped_images_array = []
    for image in mapped_images:
        image_dict = dict()
        image_dict['flickr_id'] = image.image.flickr_id
        image_dict['title'] = image.image.title
        image_dict['page'] = image.image.page.lstrip('0')
        # image_dict['url'] = image.image.flickr_small_source
        image_dict['url'] = db_tools.get_image_info(image.image.flickr_id)['imageurl']

        mapped_images_array.append(image_dict)

    collection_data['images'] = mapped_images_array
    collection_data['collection_name'] = collection_model.name

    return_object = {'collection_id': collection_id,
                     'collection_data': collection_data,
                     'collection_creator': collection_model.user.username}

    print return_object

    return render(request, 'exhibition.html', return_object)