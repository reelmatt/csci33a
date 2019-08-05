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
    # Display form with pulled-in information, that user
    # can change if they want.
    if request.method == "GET":
        try:
            book = Edition.objects.get(isbn_10=book_id)
        except Book.DoesNotExist:
            error_message(request, "That book does not exist.")
            return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

        genres = Genre.objects.all()
        context = {
            "book": book,
            "genres": genres,
        }
        print(f"Returning?? Book is {book}")
        return render(request, "books/acquire.html", context)


    try:
        edition = Edition.objects.get(isbn_10=book_id)
    except Edition.DoesNotExist:
        error_message(request, "That book does not exist.")
        return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

    # Add edition to the library
    library = Library.objects.get(pk=request.user.id)

    print(f"\n\n\n{request.POST['newGenre']}")
    print(f"{request.POST['numPages']}")

    try:
        genre = Genre.objects.get(name=request.POST["newGenre"]),
    except Genre.DoesNotExist:
        print(f"Genre did not exist.")
        genre = Genre.objects.create(
            name = request.POST["newGenre"]
        )

    print(f"\n\nwhat is the genre? {genre}")
    minutes = int(request.POST["numMinutes"])

    user_edition = UserEdition.objects.create(
        edition = edition,
        genre = Genre.objects.get(name=request.POST['newGenre']),
        num_pages = request.POST["numPages"],
        num_minutes = timedelta(seconds=(minutes * 60)),
    )

    library.editions.add(user_edition)
    library.save()

    # Create an "acquire" event
    action = Action.objects.get(action="Acquired")
    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = user_edition,
        action = action,
    )
    print(f"\n\nIN ACQUIRE, id is {book_id}")
    print(f"event saved too. it is {event}")

    return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))


def book(request, book_id):
    print(f"in book view, id is {book_id}")

    result = search_openlibrary(book_id)

    # Access a dictionary item by index
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    key = list(result.keys())[0]

    ol_book = result[key]

    try:
        title = ol_book["title"]
        print(title)
        book = Book.objects.filter(title=title).first()
        print(book)
    except Book.DoesNotExist:
        print(f"Whoops, Book does not exist")

    if book is None:
        print(f"\n\nCREATING A BOOK, and edition")
        book = add_book(request, ol_book)

    # Performing OR searches in Model.filter
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.Q
    try:
        isbn13 = Q(isbn_13=book_id)
        isbn10 = Q(isbn_10=book_id)
        editions = Edition.objects.filter(isbn10 | isbn13)
        print(f"We found editions. {editions}")
    except Edition.DoesNotExist:
        print(f"Whoops, no editions exist for id {book_id}")

    if len(editions) is 0:
        print("None editions")
        edition = add_edition(book, book_id, ol_book)

    context = {
        "book": result[key]
    }
    return render(request, "books/book.html", context)

def add_edition(book, book_id, ol_book):
    print(f"In add_edition")
    print(f"do we have a pub_year? {ol_book['publish_date']}")


    try:
        year = datetime.date(int(ol_book['publish_date']), 1, 1)
    except ValueError:
        year = None

    print(f"we have  ayear {year}")
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
        db_info = add_book_item(model, **kwargs)
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
