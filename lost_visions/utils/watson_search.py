import os
from lost_visions.models import Image, ImageText

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
import watson

__author__ = 'ubuntu'


def search():

    # watson.register(Image)
    # watson.register(ImageText)

    # print watson.get_registered_models()

    for item in watson.search('irish'):
        print item.object.title


search()