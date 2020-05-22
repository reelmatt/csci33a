# Project 3

Web Programming with Python and JavaScript

# Personal Touch

For my personal touch, I chose the first possibility listed on the assignment
spec: "allowing site administrators to mark orders as complete and allowing users to see the status of their pending or completed orders".

When signed in, a list of links appear under the user's dropdown menu in the
nav bar (upper-right). Admins see a "Placed Orders" link, which takes them to
a page that displays *all* orders placed by customers. Regular users, or
customers, will see a list of their personal order history. Either type of
user can click the link to the individual order page, which requires the
proper permissions/authentication.

Admins can update the current status of an order from an option provided in
a dropdown select. Customers can see the current status of their order.

# Implementation Notes

Menu: There were many threads on the discussion boards about the menu
requirement, including [this one](https://us.edstem.org/courses/17/discussion/514).
My menu page closely follows [that on Pinocchio's page](http://www.pinocchiospizza.net/menu.html)
with a few changes.
  1) Toppings do not appear as their own separate category. Similar to how
     the ordering process works at Grubhub and Eat24, toppings allowed on a
     given item appear on the individual item's page, where a customer can
     add it to their cart.
  2) For pricing, the pastas and salads on Pinocchio's site aren't clearly
     marked. In my implementation, I included a third, "Individual" price
     option for these items.

Registration, login, logout: Most of the code for this functionality was
taken from the django.contrib.auth package. I wrote the HTML pages for
login and registering, with some code taken from the documentation examples.
All other auth code should be noted in the comments with link to the
corresponding Django documentation.

Shopping cart: A minor deviation from the letter of the assignment spec, the
menu is accessible to all visitors, regardless of if they have an account
and are authenticated. To add items to a cart though, a user must have an
account and be logged in. If a customer tries to add an item, they will be
redirected to a login screen.

# Models

The models used for this application are thoroughly commented to illustrate
their general purpose, and in some cases, how they are used in this specific
implementation (see Status).

# Files
+ pizza/
  + settings.py - Added custom URLs for login/logout redirects
+ orders/
  + admin.py - Added my Models, customized Admin interface using example
    from Lecture 8's 'airline4' code
  + migrations/ - All generated using `python3 manage.py makemigrations`
  + models.py - All database models used for the app
    + Includes Topping, Category, Size, Item, CartItem, Status, and Order
  + static/orders/
    + styles.* - Sass/CSS files for custom styling. Only affects Menu table
  + templates/
    + orders/
      + base.html - Main template that is extended by the other files
      + cart.html - Displays items currently in a customer's cart
      + index.html - Homepage for the site, modeled/copied from Pinocchio's
        [actual site](http://www.pinocchiospizza.net)
      + item.html - Page for an individual menu item, with size and topping
        options, as appropriate. "Add to cart" button to add to customer's
        order.
      + menu.html - List of all menu items, separated out by category.
      + nav.html - Navigation bar `included` in the `base.html`.
      + order.html - Details for a given order.
      + orders.html - List of all customer's orders (for an admin), or
        customer's personal orders (for non-admins).
    + registration/
      + login.html, register.html - Used with built-in django.contrib.auth
        routes.
  + urls.py - Paths used by the application. Includes django.contrib.auth.urls.
  + views.py - Main application code.
