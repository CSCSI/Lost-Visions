from django.shortcuts import render

# Create your views here.
from django.template import RequestContext


def reimagine_home(request):
    return render(request, 'reimagine_home.html',
                  {
                      'values': 'stuff'
                  },
                  context_instance=RequestContext(request))