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
from django.views.decorators.http import require_POST
from .models import Library, Book, Edition, Event, Action, UserEdition
from users.models import User

# Library - retrieve a user's library. Login required. User and
# Library have a OneToOne relationship, meaning the Library and User
# have the same IDs.
@login_required
def library(request):
    library = None
    try:
        library = Library.objects.get(pk=request.user.id)
    except Library.DoesNotExist:
        pass

    context = {
        "library": library
    }
    return render(request, "library/library.html", context)

# Edition - Retrieve a given UserEdition to display (optionally
# customized) information about a given book.
@login_required
def edition(request, edition_id):
    context = {}
    try:
        edition = UserEdition.objects.get(
            pk=edition_id,
            libraries__user__id=request.user.id
        )
        events = Event.objects.filter(
            user=request.user.id,
            edition__id=edition_id
        )

        context = {
            "edition": edition,
            "actions": Action.objects.all(),
            "events": events,
        }

    except Exception:
        error_message(request, "That book does not exist.")

    return render(request, "library/edition.html", context)

# Add a new status
def status_update(request, edition_id):
    if request.method == "GET":
        error_message(request, "GET method not allowed.")
        return HttpResponseRedirect(reverse("edition", kwargs={"edition_id": edition_id}))

    # Get the UserEdition to create status Event for
    try:
        edition = UserEdition.objects.get(pk=edition_id, libraries__user__id=request.user.id)
    except Exception:
        pass

    # Create the event with form info
    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = edition,
        action = Action.objects.get(action=request.POST['action']),
        finished = True if request.POST['bookFinished'] == "on" else None,
    )

    context = {
        "edition": edition,
    }
    return HttpResponseRedirect(reverse("edition", kwargs={"edition_id": edition_id}))

# Display stats for a given Action in a number of days
def stats(request):
    # Default stats
    action = "Acquired"
    days = 7

    # If form is filled out, customize stats to user selection
    if request.method == "POST":
        if request.POST.get("action"):
            action = request.POST.get("action")
        if request.POST.get("numDays"):
            days = int(request.POST.get("numDays"))

    library = None
    try:
        library = Library.objects.get(pk=request.user.id)
    except Library.DoesNotExist:
        pass

    results = []
    editions = library.editions.all()

    for edition in editions:
        # Change datetime to timezone-aware var
        # https://stackoverflow.com/a/20106079
        last_day = timezone.now() - timedelta(days=days)

        result = Event.objects.filter(
            edition__id=edition.id,
            action__action__exact=action,
            creation_time__gt=last_day,
        ).all()

        if len(result) > 0:
            for item in result:
                results.append(item.edition.edition.book)

    context = {
        "library": library,
        "actions": Action.objects.all(),
        "results": results,
        "days": days,
        "selectedAction": action,
    }
    return render(request, "library/stats.html", context)

'''
Helper methods
--error_message: Add the given message to the session to be displayed
'''
def error_message(request, message):
    messages.add_message(request, messages.ERROR, message)
