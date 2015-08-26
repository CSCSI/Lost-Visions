import json
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from lost_visions.views import get_request_user
from reimagine import models


def reimagine_home(request):
    return render(request, 'reimagine_home.html',
                  {
                      'values': 'stuff'
                  },
                  context_instance=RequestContext(request))

@login_required
def entry_upload(request):
    return render(request, 'entry_upload.html',
                  {
                      'values': 'stuff'
                  },
                  context_instance=RequestContext(request))


# @csrf_exempt
@login_required
def competition_entry_store(request):

    errors = []
    messages = []
    # messages.append(json.dumps(request.POST, indent=4))
    print request.method
    if request.method == 'POST':
        if 'entry_upload_file' in request.FILES:
            try:
                uid = uuid.uuid4()

                new_entry = models.CompetitionEntry()
                new_entry.uuid = uid
                new_entry.file = request.FILES['entry_upload_file']
                new_entry.user = get_request_user(request)
                new_entry.description = request.POST.get('entry_description', '')
                new_entry.name = request.POST.get('entry_name', '')
                new_entry.datetime = request.POST.get('yearpicker', '')
                new_entry.country = request.POST.get('country', '')
                new_entry.illustration_description = request.POST.get('illustration_description', '')
                new_entry.illustration_understanding = request.POST.get('illustration_understanding', '')
                new_entry.save()
                messages.append('Your entry named "' + str(new_entry.name) + '" has been submitted.')
                messages.append('Entry reference ID : ' + str(new_entry.uuid))
            except Exception as ex:
                errors.append(ex)
        else:
            print 'no file uploaded'
            errors.append('No file selected')

    return render(request, 'thank_you.html',
                  {
                      'errors': errors,
                      'messages': messages
                  },
                  context_instance=RequestContext(request))