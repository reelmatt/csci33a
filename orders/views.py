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


    if request.user and request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        orders = user.customer_orders.all()
        print(f"User's orders are....")
        print(orders)
        print(orders[0].items.all())
        # context[cart] = orders

    context = {
        # "cart": orders[0].items.all()
    }
    return render(request, "orders/index.html", context)

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
    context = {}
    message = None
    items = None


    if request.user.is_authenticated:
        order_session = request.session.get("user_order")
        user = User.objects.get(pk=request.user.id)
        if order_session is not None:
            order = Order.objects.get(pk=order_session)
            items = order.items.all()
        elif user is not None:

            orders = user.customer_orders.all
            # selection = orders.filter(status__contains="order_placed")
            # orders = user.customer_orders.filter(status__contains="order_placed")
            print(f"WE got orders {orders}")

            selection = Order.objects.filter(customer__pk=user.id, status__status__contains="order_placed").last()
            print(f"Selection {selection}")

            if selection is not None:
                items = selection.items.all()

        else:
            message = "You haven't added any items to your cart yet."


    # https://www.geeksforgeeks.org/ternary-operator-in-python/
    context = {
        "items": items,
        "message": message,
    }

    return render(request, "orders/cart.html", context)

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

    print(f"SESSION INFO")
    print(request.session)



    print(f"itemID: {itemId}")
    print(f"price {price}")
    print(f"values {values}")
    userId = request.user.id
    user = User.objects.get(pk=userId)
    print(user)

    stored_order = request.session.get("user_order")
    print(f"DO we have a session order? {stored_order}")

    if stored_order is None:
        order = Order.objects.create(
            customer = user,
            cost = price
        )

        request.session["user_order"] = order.id
    else:
        order = Order.objects.get(pk=stored_order)


    order.items.add(item)

    cost = order.calculate_cost()
    print(f"Cost is {cost}")


    return HttpResponseRedirect(reverse("index"))
