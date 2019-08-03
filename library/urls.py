from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.library, name='library'),
    path('<int:edition_id>', views.edition, name='edition'),
    path('<int:edition_id>/<int:event_id>', views.event, name='event'),
]
