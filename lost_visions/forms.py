from django import forms

__author__ = 'ubuntu'


def tag_form_factory(image_tags):

# 'question' : forms.IntegerField(widget=forms.HiddenInput, initial=question.id),

    properties = {}

    for tag in image_tags:
        properties[image_tags[tag]] = forms.BooleanField()

    return type('TagForm', (forms.Form,), properties)

class TagForm(forms.Form):
    tag = forms.BooleanField()