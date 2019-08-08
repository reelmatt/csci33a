from django.urls import path, include
from django.apps import apps
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('<str:book_query>/<int:index>', views.work, name='work'),
]
