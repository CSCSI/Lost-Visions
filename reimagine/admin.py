from django.contrib import admin
from django.apps import apps

# Register your models here.
# from django.db.models import get_models, get_app

from reimagine.models import CompetitionEntry


class EntryAdmin(admin.ModelAdmin):
    readonly_fields = ('submit_time',)

admin.site.register(CompetitionEntry, EntryAdmin)

for model in apps.get_app_config('reimagine').get_models():
# for model in get_models(get_app('reimagine')):
    try:
        admin.site.register(model)
    except:
        pass
