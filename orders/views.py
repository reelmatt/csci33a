from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from django.contrib.auth.models import User

# Create your views here.
def index(request):

    return render(request, "orders/index.html")


# def index(request):
#     if not request.user.is_authenticated:
#         return render(request, "users/login.html", {"message": None})
#     context = {
#         "user": request.user
#     }
#     return render(request, "users/user.html", context)

'''
Replaced with Django built-in authentication views.
See documentation for more.
https://docs.djangoproject.com/en/2.2/topics/auth/default/#module-django.contrib.auth.views
'''
# def login_view(request):
#     print("WE ARE IN LOGIN VIEW")
#
#     # if not request.user.is_authenticated:
#     if request.method == "GET":
#             return render(request, "orders/login.html", {"message": None})
#
#     username = request.POST["username"]
#     password = request.POST["password"]
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return HttpResponseRedirect(reverse("index"))
#     else:
#         return render(request, "orders/login.html", {"message": "Invalid credentials."})

# def logout_view(request):
#     logout(request)
#     return render(request, "orders/login.html", {"message": "Logged out."})

# Still need a register route
def register(request):
    if request.method == "GET":
        return render(request, "registration/register.html")

    username = request.POST["username"]
    password = request.POST["password"]

    print(f"Creating user {username} with {password}")
    user = User.objects.create_user(username=username, email=None, password=password)
    print(f"MADE {user}")
    login(request, user)
    return HttpResponseRedirect(reverse("index"))


def menu(request):
    return render(request, "orders/menu.html")
