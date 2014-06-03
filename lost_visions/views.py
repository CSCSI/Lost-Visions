import ast
import json
import os
from random import randint
import re
import urllib2
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzlocal
from django.contrib import auth
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q, Min
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from nltk.corpus import wordnet as wn

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
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

        # try:
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
                # try:
                tag = models.Tag()
                tag.tag = clean(str(user_tag['tag']), strip=True)
                tag.x_percent = clean(str(user_tag['x_percent']), strip=True)
                tag.y_percent = clean(str(user_tag['y_percent']), strip=True)
                # try:
                # date_object = datetime.strptime(str(user_tag['datetime']), '%Y-%m-%dT%H:%M:%S.%f')
                date_object = parser.parse(str(user_tag['datetime']))
                tag.timestamp = date_object
                # except Exception as e3:
                #     print e3
                #     pass

                tag.tag_order = clean(str(user_tag['tag_order']), strip=True)

                if image and request_user:
                    tag.image = image
                    tag.user = request_user
                    tag.save()

                    # except Exception as e2:
                    #     print 'error 2' + str(e2)
                    #     pass

        image.views_completed += 1
        image.save()
        # except:
        #     pass

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
    # formatted_info['Download Image'] = image_info.get('imageurl', '')

    # category_data = {'question': 'Is the image a ...', 'answers': [
    #     {'name': 'map', 'id': 1, 'text': 'Map?', 'img': 'media/images/icon/map.jpg'},
    #     {'name': 'decorative_letter', 'id': 2, 'text': 'Decorative Letter?', 'img': 'media/images/icon/letter.jpg'},
    #     {'name': 'landscape', 'id': 3, 'text': 'Landscape?', 'img': 'media/images/icon/landscape.jpg'},
    #     {'name': 'portrait', 'id': 4, 'text': 'Portrait?', 'img': 'media/images/icon/portrait.jpg'},
    #     {'name': 'building', 'id': 5, 'text': 'Building?', 'img': 'media/images/icon/building.jpg'}
    #
    # ]}

    if formatted_info['Book ID'] and formatted_info['Book ID'] != '':
        illustrator_string = ''
        illustrators = models.BookIllustrator.objects.filter(book__book_identifier=formatted_info['Book ID'])
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

    return render(request, 'image.html',
                  {'image': image_info,
                   'formatted_info': formatted_info,
                   'image_id': str(image_url_part),
                   # 'category_data': category_data,
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

    # url = 'http://services.aonaware.com/DictService/DictService.asmx/MatchInDict?dictId=gcide&word=' + \
    #       word + '&strategy=prefix'
    # print url
    # resp = urllib2.urlopen(url)
    #
    # words = []
    # if resp.code == 200:
    #     data = resp.read()
    #     xml = BeautifulSoup(data)
    #
    #     for arr in xml.findAll('arrayofdictionaryword'):
    #         for dic_word in arr.findAll('dictionaryword'):
    #             for title in dic_word.findAll('word'):
    #                 if ' ' not in title.text:
    #                     words.append(title.text)
    #
    # response_data = words

    words = db_tools.search_wordnet(word)
    response_data = []
    for found_word in words:
        word_data = dict()
        word_data['label'] = found_word.lemma
        word_data['desc'] = found_word.definition
        response_data.append(word_data)

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
    return render(request,
                  'image_map.html',
                  {'image_id': image_id},
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

    return render(request,
                  'image_map.html',
                  {'image_id': image_id,
                   'image_coords_msg': 'Thank you. You may save another region, or close this window'},
                  context_instance=RequestContext(request))


@requires_csrf_token
def save_image(request):
    if request.is_ajax():
        if request.POST.get('delete_image', False):
            delete_image = models.SavedImages.objects.get(image__flickr_id=request.POST['image_id'])
            delete_image.delete()
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

        return render(request,
                      'user_home.html',
                      {'images': saved_images_dict})
    else:
        raise Http404

ICON_URL = STATIC_URL + 'media/images/icon/'

category_manager = CategoryManager()


def image_category(request):
    print request.POST

    category_data = {'question': 'Any more relevant categories?', 'answers': [
        {'name': 'yes', 'id': 0, 'text': 'Yes', 'img': ICON_URL + 'tick.png'},
        {'name': 'no', 'id': -1, 'text': 'No', 'img': ICON_URL + 'cross.png'}
    ]}

    if request.POST.get('category_id', '0') == '0':
        category_data = {'question': 'Is the image a ...', 'answers': [
            {'name': 'advert', 'id': 100, 'text': 'Advertisements?', 'img': ICON_URL + 'advert.jpg', 'wide': True},
            {'name': 'building', 'id': 200, 'text': 'Building?', 'img': ICON_URL + 'building.jpg'},
            {'name': 'people', 'id': 300, 'text': 'People?', 'img': ICON_URL + 'people.jpg'},
            {'name': 'motif', 'id': 400, 'text': 'Decoration?', 'img': ICON_URL + 'motif.jpg', 'wide': True},
            {'name': 'title_page', 'id': 500, 'text': 'Title Page?', 'img': ICON_URL + 'title_page.jpg'},
            {'name': 'map', 'id': 600, 'text': 'Map?', 'img': ICON_URL + 'map.jpg'},
            {'name': 'natural_world', 'id': 700, 'text': 'Natural World?', 'img': ICON_URL + 'nature.jpg'},
            {'name': 'scientific_drawing', 'id': 800, 'text': 'Scientific Drawing?', 'img': ICON_URL + 'science.jpg', 'wide': True},
            {'name': 'music', 'id': 900, 'text': 'Musical Score?', 'img': ICON_URL + 'music.jpg'},
            {'name': 'landscape', 'id': 1000, 'text': 'Landscape?', 'img': ICON_URL + 'landscape.jpg', 'wide': True},
            {'name': 'portrait', 'id': 1100, 'text': 'Portrait?', 'img': ICON_URL + 'portrait.jpg'},
            {'name': 'ethnographic', 'id': 1200, 'text': 'Travel/ Ethnography?', 'img': ICON_URL + 'travel.jpg', 'wide': True},
            {'name': 'words', 'id': 1300, 'text': 'Handwritten Text?', 'img': ICON_URL + 'words.jpg', 'wide': True}

        ]}

    cat_id = request.POST.get('category_id', '-1')
    #   advert
    if cat_id == '100':
        category_data = {'question': 'Is there a product/brand name?', 'answers': [
            {'name': 'yes', 'id': 101, 'text': 'Yes', 'img': ICON_URL + 'tick.png'},
            {'name': 'no', 'id': 102, 'text': 'No', 'img': ICON_URL + 'cross.png'}
        ]}

    #   building
    if cat_id == '200':
        category_data = {'question': 'Is this the buildings ...', 'answers': [
            {'name': 'interior', 'id': 201, 'text': 'Interior?', 'img': ICON_URL + 'interior.jpg'},
            {'name': 'exterior', 'id': 202, 'text': 'Exterior?', 'img': ICON_URL + 'exterior.jpg'},
            {'name': 'architectural', 'id': 203, 'text': 'Architectural Drawing?', 'img': ICON_URL + 'schematic.jpg', 'wide': True},
            ]}

    #people
    if cat_id == '300':
        category_data = {'question': 'Is the map a ...', 'answers': [
            {'name': 'individual', 'id': 301, 'text': 'Individual?', 'img': ICON_URL + 'lv-rect-station.png', 'wide': True},
            {'name': 'group', 'id': 302, 'text': 'Group?', 'img': ICON_URL + 'lv-rect-station.png'}
        ]}

    if cat_id == '301' or cat_id == '302':
        category_data = {'question': 'Are there any named historical figures?', 'answers': [
            {'name': 'no', 'id': 311, 'text': 'No', 'img': ICON_URL + 'cross.png'},
            {'name': 'add', 'id': 312, 'text': 'Add', 'img': ICON_URL + 'tick.png'}
        ]}

    if cat_id == '311' or cat_id == '312':
        category_data = {'question': 'Any Activities?', 'answers': [
            {'name': 'yes', 'id': 321, 'text': 'Yes', 'img': ICON_URL + 'tick.png'},
            {'name': 'no', 'id': 322, 'text': 'No', 'img': ICON_URL + 'cross.png'}
        ]}

    # Decorative motif
    if cat_id == '400':
        category_data = {'question': 'Is the decoration a ...', 'answers': [
            {'name': 'border', 'id': 401, 'text': 'Border?', 'img': ICON_URL + 'border.jpg', 'wide': True},
            {'name': 'emblem', 'id': 402, 'text': 'Emblem?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'coat_of_arms', 'id': 403, 'text': 'Coat of Arms?', 'img': ICON_URL + 'coat_of_arms.jpg'},
            {'name': 'decorative_letter', 'id': 404, 'text': 'Decorative Letter?', 'img': ICON_URL + 'letter.jpg', 'wide': True},
            {'name': 'motif', 'id': 401, 'text': 'Motif?', 'img': ICON_URL + 'motif.jpg'},
            ]}

    # Natural World
    if cat_id == '700':
        category_data = {'question': 'Is the image of an ...', 'answers': [
            {'name': 'animal', 'id': 701, 'text': 'Animal?', 'img': ICON_URL + 'animal.jpg'},
            {'name': 'vegetable', 'id': 702, 'text': 'Vegetable?', 'img': ICON_URL + 'lv-rect-station.png', 'wide': True},
            {'name': 'mineral', 'id': 703, 'text': 'Mineral?', 'img': ICON_URL + 'lv-rect-station.png'},
            ]}

    # Scientific Drawing
    if cat_id == '800':
        category_data = {'question': 'Is the Diagram ...', 'answers': [
            {'name': 'Geological', 'id': 801, 'text': 'Geological?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'Medical', 'id': 802, 'text': 'Medical?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'Engineering', 'id': 803, 'text': 'Engineering?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'Botanical', 'id': 804, 'text': 'Botanical?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'Zoological', 'id': 805, 'text': 'Zoological?', 'img': ICON_URL + 'lv-rect-station.png'},
            {'name': 'Archaeological', 'id': 806, 'text': 'Archaeological?', 'img': ICON_URL + 'lv-rect-station.png'}
        ]}

    if request.POST.get('category_id', '-1') == '-1':
        category_data = {'question': 'No more questions.', 'answers': []}

    try:
        image_id = request.POST.get('image_id', None)
        if image_id is not None:
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
