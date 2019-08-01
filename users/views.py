from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError

from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import User

# Route to register new users
def register(request):
    # Regular request, display form
    if request.method == "GET":
        return render(request, "registration/register.html")

    # If passwords don't match, return an error message
    if request.POST["password"] != request.POST["confirmPassword"]:
        messages.add_message(request, messages.ERROR, "Passwords don't match.")
        return render(request, "registration/register.html")

    # Otherwise, add user to database
    try:
        user = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"],
            password=request.POST["password"],
            last_name=request.POST["lastName"],
            first_name=request.POST["firstName"]
        )

        # Log them in, and send to homepage
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    # Username is not unique, throw error
    except IntegrityError as e:
        messages.add_message(request, messages.ERROR, "That username already exists.")
        return render(request, "registration/register.html")
