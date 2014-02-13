from lost_visions import forms
from lost_visions.utils.flickr import getImageTags
from lost_visions.views import get_random_image_data
from dajaxice.utils import deserialize_form

__author__ = 'ubuntu'


from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register


def get_an_image():
    # assume a problem !!!
    problem = True
    # loop to prefer failing than looping forever
    loop = 0
    while problem and loop < 20:
        loop+=1
        image_data = get_random_image_data()
        if image_data is not None:
            if 'flickr_id' in image_data:
                # this is all we care about for now
                problem = False
    # return flickr_tags['image_location']
    return image_data['flickr_large_source']


def read_category_form(form):
    CategoryForm = forms.category_form_factory()
    form = CategoryForm(deserialize_form(form))
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


def read_tags_form(form):
    TagsForm = forms.tag_form_factory({})
    tags_form = TagsForm(form)


@dajaxice_register
def load_image(request):
    dajax = Dajax()

    img_url = get_an_image()
    # print img_url

    dajax.script('change_image("' + img_url + '");')
    # dajax.assign('#result', 'value', 'hi' + image_id)
    # dajax.alert('You sent "%s"' % name)
    return dajax.json()


@dajaxice_register
def submit_tags(request, form, image_id):
    read_tags_form(form)
    print request.POST
    dajax = Dajax()

    # img_url = get_an_image()
    # print img_url

    # dajax.script('change_image("' + img_url + '");')
    dajax.script('add_new_tags();')
    # dajax.assign('#result', 'value', 'hi' + image_id)
    # dajax.alert('You sent "%s"' % name)
    return dajax.json()


@dajaxice_register
def submit_creation_techniques(request, form, image_id):
    read_category_form(form)
    print request.POST

    dajax = Dajax()
    dajax.script('add_description();')
    return dajax.json()


@dajaxice_register
def submit_free_text(request, form, image_id):
    read_category_form(form)
    print request.POST

    dajax = Dajax()
    # TODO start here
    dajax.script('add_thank_you();')
    return dajax.json()


@dajaxice_register
def submit_new_tags(request, form, image_id):
    print request.POST

    dajax = Dajax()
    # TODO start here
    dajax.script('add_categories();')
    return dajax.json()


@dajaxice_register
def submit_categories(request, form, image_id):
    read_category_form(form)
    print request.POST

    dajax = Dajax()
    dajax.script('add_creation_techniques();')
    return dajax.json()