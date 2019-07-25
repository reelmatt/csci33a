from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", include("django.contrib.auth.urls")),
    path("menu", views.menu, name="menu"),
    path("menu/<int:item_id>", views.item, name="item"),
    path("register", views.register, name="register"),
    path("add_to_cart", views.add_to_cart, name="add_to_cart")
    # Replaced with auth.urls, see above
    # path("login", views.login_view, name="login"),
    # path("login", name="login"),
    # path("logout", views.logout_view, name="logout")
    # path("logout", name="logout")
]
