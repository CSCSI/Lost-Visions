from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.db.models import get_models, get_app
from lost_visions.models import Tag, GeoTag, SavedImages, ImageText, LinkedImage, ImageMapping, SavedImageCaption, \
    ImageCollection
from lost_visions.mario_models import *
# from lost_visions.wordnet import *


class ImageSanityAdmin(admin.ModelAdmin):
    raw_id_fields = ("image",)

admin.site.register(Tag, ImageSanityAdmin)
admin.site.register(SavedImages, ImageSanityAdmin)
admin.site.register(GeoTag, ImageSanityAdmin)
admin.site.register(ImageText, ImageSanityAdmin)
admin.site.register(LinkedImage, ImageSanityAdmin)
admin.site.register(ImageMapping, ImageSanityAdmin)
# admin.site.register(SavedImageCaption, ImageSanityAdmin)


class ImageMappingInline(admin.StackedInline):
    model = ImageMapping
    raw_id_fields = ("image",)


class ImageCollectionAdmin(admin.ModelAdmin):
    # list_filter = (
    #     # ('responseid', SearchFilter),
    #     # ('responsetext', SearchFilter),
    #     # ('route_notes', SearchFilter),
    # )
    inlines = [
        ImageMappingInline
    ]
admin.site.register(ImageCollection, ImageCollectionAdmin)

for model in get_models(get_app('lost_visions')):
    try:
        admin.site.register(model)
    except:
        pass
