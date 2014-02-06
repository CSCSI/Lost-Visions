import os
from random import randint
from django.core.context_processors import csrf
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from lost_visions import models, forms
from lost_visions.utils import db_tools
from lost_visions.utils.db_tools import get_next_image_id, read_tsv_file
from lost_visions.utils.flickr import getImageTags


def home(request):
    return render_to_response('home.html')


@requires_csrf_token
def image_tags(request):
    print request.get_full_path()
    print request.POST
    c = {}
    c.update(csrf(request))
    return render_to_response('image_tags.html', context_instance=RequestContext(request))


def is_number(string):
    try:
        float(string)
        return True
    except:
        return False


def random_image(request):
    image_id = get_next_image_id()
    return image(request, image_id)


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
        if is_number(tag):
            tags[tag] = flickr_tags[tag]

    TagForm = forms.tag_form_factory(tags)
    tag_form = TagForm()

    return render(request, 'image.html',  {'image': image_info, 'tag_form': tag_form}, context_instance=RequestContext(request))


def random_file_in_folder(folder):
    files = []
    for a_file in os.listdir(folder):
        files.append( os.path.join(folder, a_file) )

    file_number = randint(0, len(files))
    return files[file_number]


def random_line_number(filename):
    lines = 0
    for _ in open(filename):
        lines += 1
    return randint(1,lines)


def grab_flickr(request):

    random_file = random_file_in_folder('/home/ubuntu/flickr_files/imagedirectory/')
    print random_file
    line_number = random_line_number(random_file)
    image_data = read_tsv_file(random_file, line_number)

    return image(request, image_data['flickr_id'])