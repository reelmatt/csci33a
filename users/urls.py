from django.urls import path, include
from . import views
from .views import LoginView

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login')
]
