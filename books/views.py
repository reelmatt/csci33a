import os
import requests
import datetime
from datetime import timedelta
from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render
from library.models import Edition, Book, Library, Author, Publisher, Genre, Action, Event, UserEdition
from django.contrib.auth.decorators import login_required
from users.models import User


'''
Main routes
--acquire: Apply any user customizations and add to user's library
--add: Create a new book to add to the database
--book: Display information about a book
'''
# Acquire route
# Will search Book Survey database to see if it finds a book matching the ID.
# If it does, it will display a form for the user to confirm/change any personal
# information they want. If not, it will report an error and redirect the user
# back to the 'book' page.
@login_required
def acquire(request, book_id):
    # Try to retrieve an edition specified by 'book_id'
    edition = retrieve_edition(request, book_id)

    if edition is None:
        return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

    # Display form with pulled-in information, that user can change if they want
    if request.method == "GET":
        context = {
            "edition": edition,
            "genres": Genre.objects.all(),
        }
        return render(request, "books/acquire.html", context)

    # Retrieve the genre, either dropdown or text entry
    if request.POST["newGenre"] != "":
        genre_args = {"name": request.POST["newGenre"]}
        genre_created = make_book_prop(Genre, **genre_args)

        if genre_created is not None:
            genre = Genre.objects.get(name=request.POST['newGenre'])
    else:
        genre = Genre.objects.get(name=request.POST['genre'])

    # Add all form fields to kwargs
    kwargs = {
        "edition": edition,
        "genre": genre,
        "num_pages": validate_form_number(request.POST["numPages"]),
    }

    # Validate the minutes entry
    minutes = validate_form_number(request.POST["numMinutes"])
    if minutes is not None:
        kwargs["num_minutes"] = timedelta(seconds=(minutes * 60))

    # Create the new UserEdition
    user_edition = UserEdition.objects.create(**kwargs)

    # Add to the library
    library = Library.objects.get(pk=request.user.id)
    library.editions.add(user_edition)
    library.save()

    # Create an 'Acquired' event and redirect
    add_event(request, user_edition)
    return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

# Add book
# Presents a form for user to enter Book/Edition information to add an
# unpublished work to the database.
@login_required
def add(request):
    # On GET, display the form to the user
    if request.method == "GET":
        return render(request, "books/add.html")

    # Otherwise POST, try to add book to database
    book = Book.objects.create(
        title = request.POST.get("title"),
        publisher = get_book_info(request.POST.get("publisher"), "publishers", Publisher),
        genre = get_book_info(request.POST.get("genre"), "genre", Genre),
    )
    authors = get_book_info(request.POST.get("author"), "authors", Author)
    book.authors.add(authors)
    book.save()

    # Validate the minutes entry
    minutes = validate_form_number(request.POST["num_minutes"])
    if minutes is not None:
        num_minutes = timedelta(seconds=(minutes * 60))

    # Create edition with form information
    edition = Edition.objects.create(
        book = book,
        isbn_10 = request.POST.get("isbn_10"),
        isbn_13 = request.POST.get("isbn_13"),
        pub_year = request.POST.get("pub_year"),
        num_pages = request.POST.get("num_pages"),
        num_minutes = num_minutes,
    )

    return HttpResponseRedirect(reverse("home"))

# Show book info
# Retrieve a book, from openlibrary or database, and render page with info
def book(request, book_id):
    result = get_openlibrary_editions([book_id])
    ol_book = result[f"OLID:{book_id}"]

    book = find_book(ol_book, request)
    edition = find_edition(book_id, book, ol_book)

    context = {
        "edition": edition,
    }
    return render(request, "books/book.html", context)

'''
Add objects to the database
--add_book: Add a book to database
--add_edition: Add an edition to database
--get_book_info: Search database if item exists, and create if it doesn't
'''
def add_book(request, ol_book):
    authors = get_book_info(ol_book, "authors", Author)
    publisher = get_book_info(ol_book, "publishers", Publisher)
    genre = get_book_info(ol_book, "subjects", Genre)
    description = ol_book.get("description")

    book = Book.objects.create(
        title = ol_book["title"],
        description = description if description else "",
        publisher = publisher,
        genre = genre,
    )

    book.authors.add(authors)
    book.save()
    return book

def add_edition(book, book_id, ol_book):
    kwargs = {
        "book": book,
    }

    year = validate_form_number(ol_book['publish_date'])
    if year is not None:
        kwargs["pub_year"] = datetime.date(year, 1, 1)

    identifiers = ol_book.get("identifiers")
    if identifiers.get("isbn_10"):
        kwargs["isbn_10"] = identifiers["isbn_10"][0]
    if identifiers.get("isbn_13"):
        kwargs["isbn_13"] = identifiers["isbn_13"][0]
    if identifiers.get("goodreads"):
        kwargs["goodreads_id"] = identifiers["goodreads"][0]
    if identifiers.get("openlibrary"):
        kwargs["openlibrary_id"] = identifiers["openlibrary"][0]
    if ol_book.get("number_of_pages"):
        kwargs["num_pages"] = ol_book["number_of_pages"]
    if ol_book.get("cover"):
        kwargs["cover"] = ol_book.get("cover").get("large")

    edition = Edition.objects.create(**kwargs)
    return edition

# Splits the attribute into a list (of one or more). It then tries to find the
# first element, which it will return if found. Otherwise, it will create a new
# element with the given info.
def get_book_info(ol_book, attr, model):
    try:
        info = ol_book.get(attr)
    except AttributeError:
        info = [{"name": ol_book}]

    db_info = None
    info_list = []

    # Parse the info into a list
    if info is not None:
        for item in info:
            if attr is "authors":
                name = item["name"].split(" ", 2)
            else:
                name = item["name"]
            info_list.append(name)
    else:
        info_list.append(ol_book)

    # Try to find the first element from the database
    try:
        if attr is "authors":
            db_info = model.objects.filter(
                first_name=info_list[0][0],
                last_name=info_list[0][1],
            ).first()
        else:
            db_info = model.objects.filter(
                name=info_list[0]
            ).first()
    except model.DoesNotExist:
        pass
    except IndexError:
        pass

    # If nothing was found, create the object
    if db_info is None and len(info_list) > 0:
        if attr is "publishers":
            model = Publisher
            kwargs = {
                "name": info_list[0],
                "location": ""
            }
        elif attr is "subjects":
            model = Genre
            kwargs = {
                "name": info_list[0]
            }
        elif attr is "authors":
            model = Author
            kwargs = {
                "first_name": info_list[0][0],
                "last_name": info_list[0][1]
            }
        db_info = model.objects.create(**kwargs)

    return db_info

# Search Open Library for a list of book_ids
def get_openlibrary_editions(book_ids):
    editions = {}
    key = ""

    url = "http://openlibrary.org/api/books?"
    for i in range(len(book_ids[0:10])):
        print(book_ids[i])
        if i is 0:
            key = f"OLID:{book_ids[i]}"
        elif i is len(book_ids[0:10]):
            key = f"{key},OLID:{book_ids[i]}"
        else:
            key = f"{key},OLID:{book_ids[i]},"

    res = requests.get(url, params={
        "bibkeys": key,
        "format": "json",
        "jscmd": "data",
    })

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()
    return data

'''
Helper methods:
--add_event: Create an 'acquire' event
--error_message: Add the given message to the session to be displayed
--find_book: Checks if a book exists in the database
--find_edition: Checks if an edition exists in the database
--make_book_prop: First checks to see if a model exists, and if not, creates it
--retrieve_edition: Error check that edition exists in database
--validate_form_number: Check form field that text parses to a number
'''
# Create an "acquire" event
def add_event(request, user_edition):
    action = Action.objects.get(action="Acquired")
    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = user_edition,
        action = action,
    )
    return

# Add the given message to the session to be displayed
def error_message(request, message):
    messages.add_message(request, messages.ERROR, message)

# Checks if a book exists in the database
def find_book(ol_book, request):
    book = None
    try:
        title = ol_book["title"]
        book = Book.objects.filter(title=title).first()
    except Book.DoesNotExist:
        pass

    if book is None:
        book = add_book(request, ol_book)

    return book

#
def find_edition(book_id, book, ol_book):
    # Performing OR searches in Model.filter
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.Q
    try:
        openlibrary = Q(openlibrary_id=book_id)
        editions = Edition.objects.filter(openlibrary)
    except Edition.DoesNotExist:
        pass

    if len(editions) is 0:
        edition = add_edition(book, book_id, ol_book)
    else:
        edition = editions.first()

    return edition

# First checks to see if a model exists, and if not, creates it
def make_book_prop(model, **kwargs):
    item = None
    try:
        item = model.objects.get(**kwargs)
    except model.DoesNotExist:
        item = model.objects.create(**kwargs)

    return item

# Error check that edition exists in database
def retrieve_edition(request, book_id):
    edition = None
    try:
        edition = Edition.objects.filter(openlibrary_id=book_id).first()
    except Edition.DoesNotExist:
        error_message(request, "That book does not exist.")

    return edition

# Check form field that text parses to a number
def validate_form_number(form_field):
    try:
        return int(form_field)
    except ValueError:
        return None
