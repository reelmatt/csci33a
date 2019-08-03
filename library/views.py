from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

from django.http import HttpResponse, HttpResponseRedirect, Http404

# Create your views here.
# Route to register new users
def library(request):
    return render(request, "library/library.html")

def edition(request):
    return render(request, "library/library.html")

def event(request):
    return render(request, "library/library.html")
