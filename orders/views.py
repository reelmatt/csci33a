from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Item, Topping, Category, Order, Status

# Display home page
def index(request):
    # Check if customer is logged in, and if any cart items
    order = get_customer_order(request.user)

    context = {
        "cart": order.items.all() if order else None
    }

    return render(request, "orders/index.html", context)

'''
Login/logout views are handled using the Django built-in authentication views.
HTML templates are found under templates/registration. See documentation for more.
https://docs.djangoproject.com/en/2.2/topics/auth/default/#module-django.contrib.auth.views
https://docs.djangoproject.com/en/2.2/topics/auth/default/#all-authentication-views

Register route is provided below.
'''
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
        return HttpResponseRedirect(reverse("index"))
    # Username is not unique, throw error
    except IntegrityError as e:
        messages.add_message(request, messages.ERROR, "That username already exists.")
        return render(request, "registration/register.html")

'''
Menu and menu item pages
    --menu
    --item
'''
# Display menu with list of items
def menu(request):
    menu = {}
    try:
        toppings = Topping.objects.all()
        categories = Category.objects.all()

        for category in categories:
            menu[category.name] = category.items.all()
    except Category.DoesNotExist:
        raise Http404("Item does not exist")

    menu["Toppings"] = toppings

    context = {
        "menu": menu
    }
    return render(request, "orders/menu.html", context)

# Individual menu item page, user customizes and adds to cart
def item(request, item_id):
    # See if the item exists, and pass info to page
    try:
        item = Item.objects.get(pk=item_id)
        return render(request, "orders/item.html", {"item": item})
    # Otherwsie, send back to menu page with error message
    except Item.DoesNotExist:
        messages.add_message(request, messages.ERROR, "That item does not exist.")
        return HttpResponseRedirect(reverse("menu"))

'''
Cart functionality
    --add_to_cart
    --cart
    --checkout
    --remove_item
'''
# Add the item to the user's cart, to be checked out later
# https://docs.djangoproject.com/en/2.2/topics/http/decorators/
@require_POST
def add_to_cart(request):
    # Pull in item ID
    itemId = request.POST["itemId"]

    # If no user, send to login and redirect back to menu
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login") + f"?next=/menu/{itemId}")

    # Find item in database
    try:
        item = Item.objects.get(pk=itemId)
    except Item.DoesNotExist:
        messages.add_message(request, messages.ERROR, "That item does not exist.")
        return HttpResponseRedirect(reverse("menu"))


    price = request.POST["price"]
    values = request.POST.getlist('toppings[]')

    # Check to see if an order is already in progress
    session_order = request.session.get("user_order")

    # There is an order started, retrieve it
    if session_order:
        order = Order.objects.get(pk=session_order)
    # No order started, create a new one
    else:
        order = Order.objects.create(
            customer = User.objects.get(pk=request.user.id),
            status = Status.objects.get(status="in_cart"),
            cost = price
        )

        # Add to session to reference later
        request.session["user_order"] = order.id


    # To new/existing order, add the new item
    order.items.add(item)

    # Update cost
    cost = order.calculate_cost()
    print(f"Cost is {cost}")
    messages.add_message(request, messages.SUCCESS, f"Added {item} to your cart.")
    return HttpResponseRedirect(reverse("menu"))

# Show contents of a user's cart, if logged in
@login_required(login_url="/login")
def cart(request):
    # Initialze order variable as None
    order = None

    # Get session to check if they exist
    order_session = request.session.get("user_order")

    # Check if order is stored in session first
    if order_session is not None:
        order = Order.objects.get(pk=order_session)

    # If not in session, check if user has any orders "in_cart"
    else:
        order = get_customer_order(request.user)

    # If an order was found, and not in session, save it there
    if order and order_session is None:
        request.session["user_order"] = order.id

    return render(request, "orders/cart.html", {"order": order})

# Process the user's cart and submit the order
def checkout(request):
    order_id = request.POST["orderId"]
    print(f"order_id is {order_id}")

    status = Status.objects.get(status="completed")
    print(f"test is {status}")

    order = Order.objects.filter(pk=order_id).update(status=status)


    print(f"order {order}")

    request.session["user_order"] = None
    return render(request, "orders/index.html")


# Remove item(s) from a user's cart
@require_POST
def remove_item(request):
    print(f"items to remove are {request.POST.getlist('items[]')}")

    try:
        order = Order.objects.get(pk=request.POST["orderId"])

        for item_id in request.POST.getlist('items[]'):
            try:
                item = Item.objects.get(pk=item_id)
                order.items.remove(item)
                messages.add_message(request, messages.SUCCESS, f"Removed {item} from your cart.")
            except Item.DoesNotExist:
                messages.add_message(request, messages.WARNING, f"Could not find item {item}.")

    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f"That order does not exist. Try again.")



    return HttpResponseRedirect(reverse("cart"))

'''
Admin pages
    view_orders -- a list of all customer orders
    order -- an individual customer's order
'''
# Admin view to see all orders placed by customers
def view_orders(request):
    # Initialize to None in case there is an exception
    orders = None

    # Try and find orders that have been placed, in_progress, or completed
    try:
        orders = Order.objects.exclude(status__status__exact="in_cart").all()
    except Order.DoesNotExist:
        messages.add_message(request, messages.WARNING, f"Could not find any orders. Try again later.")

    return render(request, "orders/orders.html", {"orders": orders})

# Admin view to see an individual order placed by a customer
def order(request, order_id):
    # Find the order, and pass through to view
    try:
        order = Order.objects.get(pk=order_id)
        statuses = Status.objects.exclude(status="in_cart").all()

        context = {
            "order": order,
            "statuses": statuses,
        }
        return render(request, "orders/order.html", context)

    # Couldn't find that order, so send back to all orders with error message
    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f"Order #{order_id} could not be found.")
        return HttpResponseRedirect(reverse("view_orders"))


def update_order_status(request, order_id):
    print(order_id)
    print(f"Do we have a form status? {request.POST['orderStatus']}")
    try:
        status = Status.objects.get(status=request.POST['orderStatus'])
        order = Order.objects.filter(pk=order_id).update(status=status)
        messages.add_message(request, messages.SUCCESS, f"Order #{order_id} status updated to {status}.")
    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f"Order #{order_id} could not be found.")

    return HttpResponseRedirect(reverse("view_orders") + f"/{order_id}")

'''
Helper methods:
    -- get_customer_order
'''
def get_customer_order(user):
    if user.is_authenticated:
        order = Order.objects.filter(customer__id__exact=user.id, status__status__exact="in_cart").first()
        print(f"User's orders are....")
        print(order)
        return order
    else:
        return None
