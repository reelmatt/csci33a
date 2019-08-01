from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView

from .forms import UserCreationForm, AuthenticationForm

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


class LoginView(LoginView):
    authentication_form = AuthenticationForm
