from django.contrib import admin
from .models import Library, Book, Edition, Author, Format, Genre, Publisher, Event, Action

# Register your models here.
admin.site.register(Library)
admin.site.register(Book)
admin.site.register(Edition)
admin.site.register(Author)
admin.site.register(Format)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Event)
admin.site.register(Action)
