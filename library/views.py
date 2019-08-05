from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from .models import Library, Book, Edition, Event

# Create your views here.
# Route to register new users
@login_required
def library(request):
    library = None
    try:
        library = Library.objects.get(pk=request.user.id)
    except Library.DoesNotExist:
        print("whoops, library dne")

    print(library)
    context = {
        "library": library
    }
    return render(request, "library/library.html", context)

@login_required
def edition(request, edition_id):
    try:
        edition = Edition.objects.get(pk=edition_id, libraries__user__id=request.user.id)
        events = Event.objects.filter(user=request.user.id, edition__id=edition_id)
    except Exception as e:
        print(f"whoops, edition does not exist\n{e}")

    print(edition)
    context = {
        "edition": edition,
        "events": events,
    }
    return render(request, "library/edition.html", context)

def event(request, edition_id, event_id):
    return render(request, "library/event.html")
