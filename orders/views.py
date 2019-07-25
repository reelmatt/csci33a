from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import User
from .models import Item, Topping, Category
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

https://docs.djangoproject.com/en/2.2/topics/auth/default/#all-authentication-views
'''

# Still need a register route
def register(request):
    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, "registration/register.html", {"form": form})

    form = AuthenticationForm(request.POST)
    if form.is_valid():
        print("\n\nYAY FORM VALID")
        form.save()
        username = request.POST["username"]
        password = request.POST["password"]
        confirmPassword = request.POST["confirmPassword"]
        first = request.POST["firstName"]
        last = request.POST["lastName"]
        email = request.POST["email"]
        if password != confirmPassword:
            print("Passwords don't match.")
            return render(request, "registration/register.html", {"message": "Passwords don't match."})
        print(f"Creating user {username} with {password}")
        user = User.objects.create_user(username=username, email=email, password=password, last_name=last, first_name=first)
        print(f"MADE {user}")
        login(request, user)
    else:
        print(f"\n\nWHOOPS, form not valid")
        raise form.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        return render(request, "registration/register.html", {"form": form})

def item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        raise Http404("Item does not exist")



    print(item)
    print(item.toppings.all())
    context = {
        "item": item,
        "toppings": item.toppings.all(),
    }

    return render(request, "orders/item.html", context)

def add_to_cart(request):
    if request.method == "POST":
        values = request.POST.getlist('toppings[]')
        print(values)
        return HttpResponseRedirect(reverse("index"))

def menu(request):
    menu = {}
    try:
        # items = Item.objects.all()
        toppings = Topping.objects.all()
        # allowed = items[2].toppings.all()

        categories = Category.objects.all()

        for category in categories:
            menu[category.name] = category.items.all()

    except Item.DoesNotExist:
        raise Http404("Item does not exist")

    print(menu)
    context = {
        "toppings": toppings,
        "categories": categories,
        "menu": menu
    }
    return render(request, "orders/menu.html", context)
