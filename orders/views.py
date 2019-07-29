from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Item, Topping, Category, Order, Status, CartItem, Size

'''
Login/logout views are handled using the Django built-in authentication views.
HTML templates are found under templates/registration. See documentation for more.
https://docs.djangoproject.com/en/2.2/topics/auth/default/#module-django.contrib.auth.views
https://docs.djangoproject.com/en/2.2/topics/auth/default/#all-authentication-views

Index/Register routes provided below.
'''
# Display home page
def index(request):
    return render(request, "orders/index.html")

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
    menu: Display a list of all categories and items offered by Pinnochio's
    item: Individual page offering customer to add/customize item to their cart
'''
# Display menu with list of items
def menu(request):
    menu = {}

    # Add all items in all categories to menu context
    categories = Category.objects.all()
    for category in categories:
        menu[category.name] = category.items.all()

    return render(request, "orders/menu.html", {"menu": menu})

# Individual menu item page, user customizes and adds to cart
# If item exists, pass info to page. Otherwise, send back to menu with error.
def item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
        return render(request, "orders/item.html", {"item": item})
    except Item.DoesNotExist:
        messages.add_message(request, messages.ERROR, "That item does not exist.")
        return HttpResponseRedirect(reverse("menu"))

'''
Cart functionality
    add_to_cart: Add item, and any extras, to customers Order (and cart)
           cart: Load the customer's current order
       checkout: Mark the customer's order as 'order_placed'
    remove_item: Delete a CartItem from the customer's order
'''
# Add the item to the user's cart, to be checked out later
# https://docs.djangoproject.com/en/2.2/topics/http/decorators/
@require_POST
def add_to_cart(request):
    # Pull in form info
    item_id = request.POST["itemId"]
    selected_toppings = request.POST.getlist('toppings[]')
    size = request.POST["size"]

    # If no user, send to login and redirect back to menu
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login") + f"?next=/menu/{item_id}")

    # Find menu item in database
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        messages.add_message(request, messages.ERROR, "That menu item does not exist.")
        return HttpResponseRedirect(reverse("menu"))

    # Check user selected a valid number of toppings
    if not valid_num_toppings(item, selected_toppings):
        messages.add_message(request, messages.ERROR, f"This item can only have {item.num_toppings} toppings. You selected {len(selected_toppings)}.")
        return HttpResponseRedirect(reverse("menu") + f"/{item_id}")

    # All info is valid, so add create/access CartItem and Order
    order = get_session_order(request)
    cart_item = new_cart_item(item, size, selected_toppings)

    # Add new CartItem to the Order
    order.items.add(cart_item)
    order.cost = order.cost + cart_item.cost()
    order.save()

    print(f"\n\nADDING TO CART, order cost is {order.cost}")
    # Display a success message
    messages.add_message(request, messages.SUCCESS, f"Added {item} to your cart.")
    return HttpResponseRedirect(reverse("menu"))

# Show contents of a user's cart, if logged in
@login_required(login_url="/login")
def cart(request):
    # Initialze order variable as None
    order = None

    # Get session to check if order exists
    order_session = request.session.get("user_order")

    # Get order saved in session, or get last saved cart
    if order_session is not None:
        order = Order.objects.get(pk=order_session)
    else:
        order = get_customer_order(request.user)

    # If an order was found, and not in session, save it there
    if order and order_session is None:
        request.session["user_order"] = order.id

    return render(request, "orders/cart.html", {"order": order})

# Process the user's cart and submit the order
@require_POST
def checkout(request):
    # Get the order to checkout
    order_id = request.POST["orderId"]

    # Update status in database
    status = Status.objects.get(status="order_placed")
    order = Order.objects.filter(pk=order_id).update(status=status)

    # Reset session for next order
    request.session["user_order"] = None
    return render(request, "orders/index.html")

# Remove item(s) from a user's cart
@require_POST
def remove_item(request):
    # Get order and items to delete
    order_id = request.POST["orderId"]
    to_delete = request.POST.getlist('items[]')

    try:
        order = Order.objects.get(pk=order_id)
        items = CartItem.objects.filter(orders__pk__exact=order_id, pk__in=to_delete).all()

        # Calculate price of all items being removed
        cost = 0
        for item in items:
            cost = cost + item.cost()

        # Update the order cost, and remove items from order
        order.cost = order.cost - cost
        order.save()
        items.delete()
    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f"That order does not exist. Try again.")
    except CartItem.DoesNotExist:
        messages.add_message(request, messages.WARNING, f"Could not find item {item}.")

    messages.add_message(request, messages.SUCCESS, f"Removed items from your cart.")
    return HttpResponseRedirect(reverse("cart"))

'''
Admin pages
              order: an individual order
update_order_status: change the status of a given order
                        ('order_placed', 'in_progress', 'completed')
        view_orders: a list of orders (admin = all orders; customer = personal orders)

'''
# Admin view to see all orders placed by customers
def view_orders(request):
    # Initialize to None in case there is an exception
    orders = None


    if request.user.is_staff:
        # Try and find orders that have been placed, in_progress, or completed
        try:
            orders = Order.objects.exclude(status__status__exact="in_cart").all()
        except Order.DoesNotExist:
            messages.add_message(request, messages.WARNING, f"Could not find any orders. Try again later.")
    elif request.user.is_authenticated:
        try:
            orders = Order.objects.filter(customer__id__exact=request.user.id).exclude(status__status__exact="in_cart").all()
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

def get_session_order(request):
    order = None

    # Check to see if an order is already in progress
    session_order = request.session.get("user_order")

    # Get order saved in session, or create a new one
    if session_order:
        order = Order.objects.get(pk=session_order)
    else:
        order = Order.objects.create(
            customer = User.objects.get(pk=request.user.id),
            status = Status.objects.get(status="in_cart"),
            cost = 0
        )

        # Add to session to reference later
        request.session["user_order"] = order.id

    return order

def valid_num_toppings(item, toppings):

    str = item.category.name
    print(f"\n\n{str}")
    print(f"bool test is {'Pizzas' in str}")
    if "Pizzas" in str:
        if item.num_toppings == len(toppings):
            return True
    elif item.num_toppings >= len(toppings):
        print(f"OTHER and numbers okay, {item.num_toppings} >= {len(toppings)}")
        return True

    return False



def new_cart_item(item, size, selected_toppings):
    # Create new CartItem
    cart_item = CartItem.objects.create(
        size = Size.objects.get(size=size),
        item = item,
    )

    # Add selected toppings
    toppings = Topping.objects.filter(name__in=selected_toppings)
    cart_item.toppings.set(toppings)

    return cart_item
