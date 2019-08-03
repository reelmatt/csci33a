from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.library, name='library'),
]
