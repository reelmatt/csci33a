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

# Acquire route
# Will search Book Survey database to see if it finds a book matching the ID
# If it doesn't, it will add a copy to the database. For all requests, it will
# then display a form for the user to confirm/change any personal information
# they want.
@login_required
def acquire(request, book_id):

    edition = retrieve_edition(request, book_id)

    if edition is None:
        return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

    # Display form with pulled-in information, that user
    # can change if they want.
    if request.method == "GET":
        genres = Genre.objects.all()
        context = {
            "edition": edition,
            "genres": genres,
        }
        return render(request, "books/acquire.html", context)

    # Add edition to the library
    library = Library.objects.get(pk=request.user.id)

    genre_args = {"name": request.POST["newGenre"]}
    genre = make_book_prop(Genre, **genre_args)


    kwargs = {
        "edition": edition,
        # "genre": genre,
        "genre": Genre.objects.get(name=request.POST['newGenre']),
    }

    minutes = book_minutes(request)
    try:
        pages = int(request.POST["numPages"])
    except ValueError:
        pages = None

    if pages is not None:
        kwargs["num_pages"] = pages
    if minutes is not None:
        kwargs["num_minutes"] = minutes

    user_edition = add_book_item(UserEdition, **kwargs)


    library.editions.add(user_edition)
    library.save()

    add_event(request, user_edition)

    return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

def book_minutes(request):
    try:
        minutes = int(request.POST["numMinutes"])
        return timedelta(seconds=(minutes * 60))
    except ValueError:
        return None


def retrieve_edition(request, book_id):
    edition = None
    try:
        edition = Edition.objects.get(isbn_10=book_id)
    except Edition.DoesNotExist:
        # Add book, and try again before reporting error
        error_message(request, "That book does not exist.")

    return edition

# Create an "acquire" event
def add_event(request, user_edition):
    action = Action.objects.get(action="Acquired")
    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = user_edition,
        action = action,
    )
    return

# First checks to see if a model exists, and if not, creates it
def make_book_prop(model, **kwargs):
    item = None
    try:
        item = model.objects.get(**kwargs)
    except model.DoesNotExist:
        print("model did not exist.")
        item = model.objects.create(**kwargs)

    return item

def book(request, book_id):
    result = search_openlibrary(book_id)

    # Access a dictionary item by index
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    try:
        key = list(result.keys())[0]
    except IndexError:
        error_message(request, f"We don't have a book by that id - {book_id}.")
        return HttpResponseRedirect(reverse("search"))
    ol_book = result[key]

    book = find_book_book(ol_book, request)
    edition = find_book_edition(book_id, book, ol_book)

    context = {
        "edition": edition
    }
    return render(request, "books/book.html", context)

def add_edition(book, book_id, ol_book):
    print(f"In add_edition")
    print(f"do we have a pub_year? {ol_book['publish_date']}")

    try:
        year = datetime.date(int(ol_book['publish_date']), 1, 1)
    except ValueError:
        year = None

    edition = Edition.objects.create(
        book = book,
        isbn_10 = book_id,
        pub_year = year
    )

    print(f"returning with a new edition. {edition}")
    return edition

def add_book(request, ol_book):
    authors = get_book_info(ol_book, "authors", Author)
    publisher = get_book_info(ol_book, "publishers", Publisher)
    genre = get_book_info(ol_book, "subjects", Genre)

    book = Book.objects.create(
        title = ol_book["title"],
        publisher = publisher,
        genre = genre,
    )

    book.authors.add(authors)
    book.save()
    print(f"Returning from add_book, result was {book}")
    return book

def find_book_book(ol_book, request):
    try:
        title = ol_book["title"]
        book = Book.objects.filter(title=title).first()
    except Book.DoesNotExist:
        print(f"Whoops, Book does not exist")

    if book is None:
        book = add_book(request, ol_book)

    return book

def find_book_edition(book_id, book, ol_book):
    # Performing OR searches in Model.filter
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.Q
    try:
        isbn13 = Q(isbn_13=book_id)
        isbn10 = Q(isbn_10=book_id)
        editions = Edition.objects.filter(isbn10 | isbn13)
    except Edition.DoesNotExist:
        print(f"Whoops, no editions exist for id {book_id}")

    if len(editions) is 0:
        edition = add_edition(book, book_id, ol_book)
    else:
        edition = editions.first()

    return edition

def get_book_info(ol_book, attr, model):
    info = ol_book.get(attr)
    db_info = None
    info_list = []

    if info is not None:
        for item in info:
            if attr is "authors":
                name = item["name"].split(" ", 2)
            else:
                name = item["name"]
            info_list.append(name)

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
        print("whoops, model does not exist.")
    except IndexError:
        print("Genres do not exist.")

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

    print(f"Returning from get_book_info, result is {db_info}")
    return db_info

def add_book_item(model, **kwargs):
    print(f"adding args {kwargs}")
    return model.objects.create(**kwargs)

def search_openlibrary(book_id):
    url = "http://openlibrary.org/api/books?"
    key = f"ISBN:{book_id}"

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


def error_message(request, message):
    messages.add_message(request, messages.ERROR, message)
