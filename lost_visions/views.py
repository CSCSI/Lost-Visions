from django.core.context_processors import csrf
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from lost_visions import models, forms
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


@requires_csrf_token
def image(request, image_id):
    print image_id
    image_for_id = models.Image.objects.get(identifier=image_id)

    image_info = dict()

    image_info['imageurl'] = image_for_id.imageurl
    image_info['book_title'] = image_for_id.book.title
    image_info['author'] = image_for_id.book.author.name
    image_info['tags'] = image_for_id.tags.split(';')

    image_url = image_for_id.imageurl
    #cut image ID from image URL
    imageID = (image_url.rsplit('/', 1)[1]).split('_')[0]
    #get Flickr tags for this image
    tags = getImageTags('http://www.flickr.com/photos/britishlibrary/' + imageID)

    TagForm = forms.tag_form_factory(tags)
    tag_form = TagForm()

    return render(request, 'image.html',  {'image': image_info, 'tag_form' : tag_form}, context_instance=RequestContext(request))
