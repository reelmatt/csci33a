from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST

from django.contrib.auth.models import User
from .models import Item, Topping, Category, Order

# Display home page
def index(request):
    return render(request, "orders/index.html")

'''
Login/logout views are handled using the Django built-in authentication views.
See documentation for more.
https://docs.djangoproject.com/en/2.2/topics/auth/default/#module-django.contrib.auth.views
https://docs.djangoproject.com/en/2.2/topics/auth/default/#all-authentication-views
'''

# Route to register new users
def register(request):
    # Regular request, display form
    if request.method == "GET":
        return render(request, "registration/register.html")

    # Otherwise, POSTed form, check validity and create user
    first = request.POST["firstName"]
    last = request.POST["lastName"]
    email = request.POST["email"]
    username = request.POST["username"]
    password = request.POST["password"]
    confirmPassword = request.POST["confirmPassword"]

    # If passwords don't match, return an error
    if password != confirmPassword:
        return render(request, "registration/register.html", {"message": "Passwords don't match."})

    # Otherwise, add user to database
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        last_name=last,
        first_name=first
    )

    # Log them in, and send to homepage
    login(request, user)
    return HttpResponseRedirect(reverse("index"))


# Display menu with list of items
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

    menu["Toppings"] = toppings

    print(menu)
    context = {
        "toppings": toppings,
        "categories": categories,
        "menu": menu
    }
    return render(request, "orders/menu.html", context)

#
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

# Show contents of a user's cart
def cart(request):

    return render(request, "orders/cart.html")

# Admin view to see all orders placed by customers
def view_orders(request):
    try:
        orders = Order.objects.all()
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    print(orders)
    context = {
        "orders": orders,
    }
    return render(request, "orders/orders.html", context)

# Admin view to see an individual order placed by a customer
def order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    print(order)
    print(order.items.all())
    context = {
        "order": order,
    }

    return render(request, "orders/order.html", context)

# Process the user's cart and submit the order
def checkout(request):
    return render(request, "orders/index.html")

# Add the item to the user's cart, to be checked out later
# https://docs.djangoproject.com/en/2.2/topics/http/decorators/
@require_POST
def add_to_cart(request):
    itemId = request.POST["itemId"]
    price = request.POST["price"]
    values = request.POST.getlist('toppings[]')

    try:
        item = Item.objects.get(pk=itemId)
    except Item.DoesNotExist:
        print("whoops")

    print(itemId)
    print(price)
    print(values)
    userId = request.user.id
    user = User.objects.get(pk=userId)
    print(user)

    order = Order.objects.create(
        customer = user,
        cost = price
    )

    order.items.add(item)
    return HttpResponseRedirect(reverse("index"))
