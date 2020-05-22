from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", include("django.contrib.auth.urls")),
    path("add_to_cart", views.add_to_cart, name="add_to_cart"),
    path("cart", views.cart, name="cart"),
    path("checkout", views.checkout, name="checkout"),
    path("orders", views.view_orders, name="view_orders"),
    path("orders/<int:order_id>", views.order, name="order"),
    path("orders/<int:order_id>/update", views.update_order_status, name="update_order_status"),
    path("menu", views.menu, name="menu"),
    path("menu/<int:item_id>", views.item, name="item"),
    path("register", views.register, name="register"),
    path("remove_item", views.remove_item, name="remove_item")
]
