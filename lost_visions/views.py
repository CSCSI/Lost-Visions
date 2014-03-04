import os
from random import randint
from django.contrib.auth import authenticate
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from lost_visions import models, forms
from lost_visions.forms import TestForm
from lost_visions.utils import db_tools
from lost_visions.utils.db_tools import get_next_image_id, read_tsv_file
from lost_visions.utils.flickr import getImageTags


def home(request):
    return render_to_response('home.html')


@requires_csrf_token
def image_tags(request):
    print request.get_full_path()
    # print request.POST['question']

    if request.method == 'POST':
        print request.POST
        test_form = TestForm(request.POST)
        # print test_form.question
        if test_form.is_valid():
            print test_form.is_valid()
            # print test_form.cleaned_data['question']
        else:
            print 'not valid'
            print request.POST

    # return render_to_response('image.html', context_instance=RequestContext(request))
    return random_image(request)

def is_number(string):
    try:
        float(string)
        return True
    except:
        return False


def random_image(request):
    image_id = get_next_image_id()
    return image(request, image_id)


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

    image_info = db_tools.get_image_info(image_id)

    if image_info is None:
        image_url_part = image_id
        image_info = dict()
    else:
        print image_info['imageurl']
        image_url_part = (image_info['imageurl'].rsplit('/', 1)[1]).split('_')[0]

    #cut image ID from image URL
    #get Flickr tags for this image
    flickr_tags = getImageTags('http://www.flickr.com/photos/britishlibrary/' + image_url_part, size='z')

    if not 'imageurl' in image_info:
        image_info['imageurl'] = flickr_tags['image_location']

    tags = {}
    for tag in flickr_tags:
        if is_number(tag) and is_user_tag(flickr_tags[tag]):
            tags[tag] = flickr_tags[tag]
        else:
            image_info[tag] = flickr_tags[tag].replace('&quot;', '"')

    TagForm = forms.tag_form_factory(tags)
    tag_form = TagForm()

    CategoryForm = forms.category_form_factory()
    category_form = CategoryForm()

    CreationTech = forms.creation_technique_form_factory()
    create_tech = CreationTech()

    return render(request, 'image.html',
                  {'image': image_info,
                   'image_id': image_url_part,
                   'tag_form': tag_form,
                   'category_form': category_form,
                   'create_tech_form': create_tech},
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
    return render_to_response('about_us.html')


def login(request):
    return render_to_response('login.html')


def do_login(request):

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:

            print("User is valid, active and authenticated")
            success = True
            msg = 'You have successfully logged in'
        else:
            print("The password is valid, but the account has been disabled!")
            success = False
            msg = 'This account has been disabled. Please contact the Lost-Visions team.'

        return render_to_response('home.html', {'login_success': success, 'msg': msg})

    else:
        msg = 'Username and Password combination not recognised, please try again.'
        success = False
    return render_to_response('login.html', {'login_success': success, 'msg': msg})


def logout(request):
    if request.user.is_authenticated():
        logout(request)
        msg = 'You have successfully logged out'
        logout_success = True
    #do logout
    return render_to_response('home.html', {'logout_success': logout_success, 'msg': msg})


def signup(request):
    return render_to_response('signup.html')
