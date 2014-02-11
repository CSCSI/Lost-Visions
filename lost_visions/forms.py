from django import forms

__author__ = 'ubuntu'


def tag_form_factory(image_tags):

# 'question' : forms.IntegerField(widget=forms.HiddenInput, initial=question.id),

    properties = {}

    for tag in image_tags:
        properties[image_tags[tag]] = forms.BooleanField(initial=True)

    return type('TagForm', (forms.Form,), properties)


def creation_technique_form_factory():
    techniques = ['photography', 'etching', 'printing']
    properties = {}
    for tech in techniques:
        properties[tech] = forms.BooleanField(initial=False)

    return type('TechForm', (forms.Form,), properties)


def category_form_factory():

    def clean(self):
        print 'this ran???'
        print self.cleaned_data
        return self.cleaned_data

    # properties = {}
    properties = dict(clean=lambda self: clean(self))

    categories = dict()
    categories['cycling'] = 'cycling'
    categories['title pages'] = 'cover'
    categories['castles'] = 'castle'
    categories['decorative paper'] = "decorative papers"
    categories['ships'] = 'ship'
    categories['technology'] = 'technology'
    categories['science fiction'] = 'sciencefiction'
    categories['childrens book'] = "children's book illustration"
    categories['illustrated letters and typography'] = 'letter'
    categories['decoration'] = 'decoration'
    categories['maps'] = 'map'
    categories['fashion and costumes'] = 'fashion'
    categories['portraits'] = 'portrait'
    categories['christmas'] = 'christmas'

    for tag in categories:
        properties[categories[tag]] = forms.BooleanField(initial=False)

    # properties['clean'] = clean()
    return type('CategoryForm', (forms.Form,), properties)


class TestForm(forms.Form):
    question = forms.BooleanField()

