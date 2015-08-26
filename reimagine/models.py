from django.db import models
from lost_visions.models import LostVisionUser
# import uuid

import datetime
YEAR_CHOICES = []
for r in range(1900, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r, r))

class CompetitionEntry(models.Model):

    def get_upload_directory(self, filename):
        # uid = uuid.uuid4()
        return '/tmp/reimagine/entries/' + str(self.uuid) + '/' + filename

    file = models.FileField(upload_to=get_upload_directory)
    year_of_birth = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    description = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    user = models.ForeignKey(LostVisionUser)
    uuid = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)
    illustration_description = models.TextField(blank=True, null=True)
