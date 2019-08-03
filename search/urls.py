from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('<slug:book_id>', views.book, name='book')
]
