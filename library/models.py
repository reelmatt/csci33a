from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Stores a collection of Books (Editions) for a given user
class Library(models.Model):
    # Who is the 'owner' of the library
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="library", primary_key=True)

    # An assortment of 'Editions', or more-specific book information
    editions = models.ManyToManyField('Edition', related_name="libraries", blank=False)

    # Optional customizations made by user if their version deviates from the
    # 'standard' edition info found on Open Library or Goodreads
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, related_name="libraries", blank=True, null=True)
    num_pages = models.PositiveIntegerField(blank=True, null=True)
    num_minutes = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}'s Library'"

# The most basic representation of a Book
class Book(models.Model):
    title = models.CharField(max_length=256)
    authors = models.ManyToManyField('Author', related_name="books")
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, related_name="books")
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, related_name="editions")

    def __str__(self):
        return f"{self.title}"

# A more specific representation of an Edition of a book
class Edition(models.Model):
    # The base book
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="editions")

    # Book IDs
    isbn_10 = models.CharField(max_length=10, blank=True)
    isbn_13 = models.CharField(max_length=13, blank=True)
    goodreads_id = models.CharField(max_length=20, blank=True)
    openlibrary_id = models.CharField(max_length=20, blank=True)

    # Edition-specific book information
    pub_year = models.DateField(blank=True, null=True)
    format = models.ForeignKey('Format', on_delete=models.CASCADE, blank=True, null=True, related_name="editions")
    num_pages = models.PositiveIntegerField(blank=True, null=True)
    num_minutes = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"{self.book}-{self.isbn_10}"

# Author model (just first/last name for now)
class Author(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Format model - e.g. Hardcover, paperback, ebook, audiobook, etc.
class Format(models.Model):
    format = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.format}"

# Genre model (just a 'name' for now; could expand to include sub-genre, etc.)
class Genre(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

# Information about the book's Publisher
class Publisher(models.Model):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.name}"

# Model to log and track user 'events' for a given book edition
class Event(models.Model):
    # Who made the event (also ties directly to a library)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="events")

    # What action was taken?
    action = models.ForeignKey('Action', on_delete=models.CASCADE, related_name="events")

    # Common information that changes for a given event
    # Doesn't always change, can be blank
    pages_read = models.PositiveIntegerField(blank=True, null=True)
    minutes_listened = models.DurationField(blank=True, null=True)
    finished = models.BooleanField(blank=True, null=True)

    # Keep track of creation/modification times
    creation_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.action} - {self.creation_time}"

# Action model
class Action(models.Model):
    # e.g. - Acquired, Read, TBR, DNF, Returned, etc.
    action = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.action}"
