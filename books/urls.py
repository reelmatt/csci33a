from django.urls import path, include
from . import views

urlpatterns = [
    path('<slug:book_id>', views.book, name='book'),
    path('<slug:book_id>/acquire', views.acquire, name='acquire'),
]
