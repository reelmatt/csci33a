from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.library, name='library'),
    path('<int:edition_id>', views.edition, name='edition'),
    path('<int:edition_id>/<int:event_id>', views.event, name='event'),
    path('<int:edition_id>/post', views.status_update, name='status update'),
    path('stats', views.stats, name='stats')
]
