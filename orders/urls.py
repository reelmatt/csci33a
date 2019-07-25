from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", include("django.contrib.auth.urls")),
    path("menu", views.menu, name="menu"),
    path("register", views.register, name="register"),

    # Replaced with auth.urls, see above
    # path("login", views.login_view, name="login"),
    # path("login", name="login"),
    # path("logout", views.logout_view, name="logout")
    # path("logout", name="logout")
]
