import datetime
from datetime import timedelta
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
import pytz
from django.contrib import messages
from django.db import IntegrityError
from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from .models import Library, Book, Edition, Event, Action, UserEdition
from users.models import User
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
    context = {}
    try:
        edition = UserEdition.objects.get(pk=edition_id, libraries__user__id=request.user.id)
        events = Event.objects.filter(user=request.user.id, edition__id=edition_id)
        print(edition)
        context = {
            "edition": edition,
            "actions": Action.objects.all(),
            "events": events,
        }

    except Exception as e:
        print(f"whoops, edition does not exist\n{e}")
        error_message(request, "That book does not exist.")


    return render(request, "library/edition.html", context)

def status_update(request, edition_id):
    try:
        edition = UserEdition.objects.get(pk=edition_id, libraries__user__id=request.user.id)
    except Exception as e:
        print("whoops")

    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = edition,
        action = Action.objects.get(action=request.POST['action']),
    )

    context = {
        "edition": edition,
    }
    return HttpResponseRedirect(reverse("edition", kwargs={"edition_id": edition_id}))

def stats(request):
    # Default stats
    action = "Acquired"
    days = 7

    if request.method == "POST":
        print("updating values...")
        if request.POST.get("action"):
            action = request.POST.get("action")
        if request.POST.get("numDays"):
            days = int(request.POST.get("numDays"))

        print(f"action is {action} and number of days are {days}")

    library = None
    try:
        library = Library.objects.get(pk=request.user.id)
    except Library.DoesNotExist:
        print("whoops, library dne")


    acquired = []
    editions = library.editions.all()

    for edition in editions:
        # print(edition.events.all())

        # Change datetime to timezone-aware var
        # https://stackoverflow.com/a/20106079

        last_day = timezone.now() - timedelta(days=days)

        result = Event.objects.filter(
            edition__id=edition.id,
            action__action__exact=action,
            creation_time__gt=last_day,
        ).all()

        if len(result) > 0:
            # print(f"\n{result}")
            # print(f"\n{result.values()}")

            for item in result:
                # print(item.edition.edition.book)
                acquired.append(item.edition.edition.book)

            # acquired.append(result.values())


    # print(f"acquired: {acquired}")
    print(f"\nacquired length {len(acquired)}")

    context = {
        "library": library,
        "actions": Action.objects.all(),
        "acquired": acquired,
    }
    return render(request, "library/stats.html", context)

def event(request, edition_id, event_id):
    return render(request, "library/event.html")



def error_message(request, message):
    messages.add_message(request, messages.ERROR, message)
