# Load Django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

# Models
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
        error_message(request, "The passwords don't match.")
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
        error_message(request, "That username already exists.")
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
        sizes = Size.objects.all()
        selection = []
        for size in sizes:
            # getattr() requires a string, but did not allow formatted style
            tmp = f"price_{size.size}"
            price = getattr(item, tmp)
            selection.append((size, price))

        context = {
            "item": item,
            "selection": selection,
        }
        return render(request, "orders/item.html", context)
    except Item.DoesNotExist:
        error_message(request, "That item does not exist.")
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
    size = request.POST.get("size")

    # If no user, send to login and redirect back to menu
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login") + f"?next=/menu/{item_id}")

    # Find menu item in database
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        error_message(request, "That menu item does not exist.")
        return HttpResponseRedirect(reverse("menu"))

    # Check customer selected a size option
    if not size:
        error_message(request, "Please select a size option.")
        return HttpResponseRedirect(reverse("menu") + f"/{item_id}")

    # Check customer selected a valid number of toppings
    if not valid_num_toppings(item, selected_toppings):
        if item.num_toppings < len(selected_toppings):
            error_message(request, "Please remove some toppings to add to your cart.")
        else:
            error_message(request, f"The item you selected requires {item.num_toppings} toppings.")
        return HttpResponseRedirect(reverse("menu") + f"/{item_id}")

    # All info is valid, so add create/access CartItem and Order
    order = get_session_order(request)
    cart_item = new_cart_item(item, size, selected_toppings)

    # Add new CartItem to the Order, update cost
    order.items.add(cart_item)
    order.cost = order.cost + cart_item.cost()
    order.save()

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
    try:
        if order_session is not None:
            order = Order.objects.get(pk=order_session)
        else:
            order = get_customer_order(request.user)
    except Order.DoesNotExist:
        error_message(request, "Sorry, but we could not find your order.")
        request.session["user_order"] = None

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

    messages.add_message(request, messages.SUCCESS, "You have successfully placed your order. Check your order history to see when it is ready.")
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
        error_message(request, "That order does not exist. Try again.")
    except CartItem.DoesNotExist:
        error_message(request, f"Could not find item {item}.")

    messages.add_message(request, messages.SUCCESS, f"Removed items from your cart.")
    return HttpResponseRedirect(reverse("cart"))

'''
Order history/status
-- order:
    an individual order
-- update_order_status:
    change the status of a given order ('order_placed', 'in_progress', 'completed')
-- view_orders:
    a list of orders (admin = all orders; customer = personal orders)

'''
# View to see all orders placed by customers
def view_orders(request):
    # Initialize to None in case there is an exception
    orders = None

    # For admins, show all customer orders
    if request.user.is_staff:
        # Try and find orders that have been placed, in_progress, or completed
        try:
            orders = Order.objects.exclude(status__status__exact="in_cart").all()
        except Order.DoesNotExist:
            error_message(request, "Could not find any orders. Try again later.")

    # If a customer, show just their orders
    elif request.user.is_authenticated:
        try:
            orders = Order.objects.filter(customer__id__exact=request.user.id).exclude(status__status__exact="in_cart").all()
        except Order.DoesNotExist:
            error_message(request, "Could not find any orders. Try again later.")

    return render(request, "orders/orders.html", {"orders": orders})

# View to see an individual order placed by a customer
def order(request, order_id):
    try:
        order = None

        # If staff, return the order
        if request.user.is_staff:
            order = Order.objects.get(pk=order_id)

        # If a customer, check the order belongs to them
        elif request.user.is_authenticated:
            order = Order.objects.filter(pk=order_id, customer__pk__exact=request.user.id).first()

            # If it doesn't, display an error
            if not order:
                error_message(request, "Could not find any orders by you with that ID.")

        # Pass order, and list of available statuses to view
        context = {
            "order": order,
            "statuses": Status.objects.exclude(status="in_cart").all(),
        }
        return render(request, "orders/order.html", context)

    # Couldn't find that order, so send back to all orders with error message
    except Order.DoesNotExist:
        error_message(request, f"Order #{order_id} could not be found.")
        return HttpResponseRedirect(reverse("view_orders"))

# Allow a admin to update the status of an order
@require_POST
@permission_required('user.is_staff', login_url='/login')
def update_order_status(request, order_id):
    try:
        status = Status.objects.get(status=request.POST['orderStatus'])
        order = Order.objects.filter(pk=order_id).update(status=status)
        messages.add_message(request, messages.SUCCESS, f"Order #{order_id} status updated to {status}.")
    except Order.DoesNotExist:
        error_message(request, f"Order #{order_id} could not be found.")

    return HttpResponseRedirect(reverse("view_orders") + f"/{order_id}")

'''
Helper methods:
-- error_message: Uses Django's message module to output error message
-- get_customer_order: Retrieve's a logged-in user's most recent order
-- get_session_order: Check's the session to see if an order exists; if not
    the method will create a new order and store it in the session
-- new_cart_item: Create a new cart item to add to an order with given size and
    toppings
-- valid_num_toppings: Checks the number of toppings selected against the allowed
    amount for a given item.
'''
def error_message(request, message):
    messages.add_message(request, messages.ERROR, message)

def get_customer_order(user):
    if user.is_authenticated:
        order = Order.objects.filter(customer__id__exact=user.id, status__status__exact="in_cart").last()
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

def new_cart_item(item, size, selected_toppings):
    # Split form field to access Size field
    size_str = size.split('_')[1]

    # Create new CartItem
    cart_item = CartItem.objects.create(
        size = Size.objects.get(size=size_str),
        item = item,
    )

    # Add selected toppings
    toppings = Topping.objects.filter(name__in=selected_toppings)
    cart_item.toppings.set(toppings)

    return cart_item

def valid_num_toppings(item, toppings):
    str = item.category.name

    # If item category includes Pizza, toppings must match
    if "Pizza" in item.category.name:
        if item.num_toppings == len(toppings):
            return True
    # Otherwise, toppings cannot exceed item's max
    elif item.num_toppings >= len(toppings):
        return True

    return False
