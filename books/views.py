import os
import requests
import datetime

from django.apps import apps
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render
from library.models import Edition, Book, Library, Author, Publisher, Genre, Action, Event
from django.contrib.auth.decorators import login_required
from users.models import User
# Acquire route
# Will search Book Survey database to see if it finds a book matching the ID
# If it doesn't, it will add a copy to the database. For all requests, it will
# then display a form for the user to confirm/change any personal information
# they want.
@login_required
def acquire(request, book_id):
    try:
        edition = Edition.objects.get(isbn_10=book_id)
    except Edition.DoesNotExist:
        error_message(request, "That book does not exist.")
        return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))

    # Add edition to the library
    library = Library.objects.get(pk=request.user.id)
    library.editions.add(edition)
    library.save()

    # Create an "acquire" event
    action = Action.objects.get(action="Acquired")
    event = Event.objects.create(
        user = User.objects.get(pk=request.user.id),
        edition = edition,
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
    # Performing OR searches in Model.filter
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.Q
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
    authors = get_author(ol_book)
    print(f"back in add_book, author is {authors}")

    publisher = get_publisher(ol_book)
    print(f"back in add_book, publisher is {publisher}")

    genre = get_genre(ol_book)
    print(f"back in add_book, genre is {genre}")

    book = Book.objects.create(
        title = ol_book["title"],
        publisher = publisher,
        genre = genre,
    )

    book.authors.add(authors)
    book.save()
    print(f"Returning from add_book, result was {book}")
    return book

def add_author(first, last):
    print(f"In add_author, first is {first} and last is {last}")

    author = Author.objects.create(
        first_name = first,
        last_name = last,
    )


    return author


def get_author(ol_book):
    print("\nIn get_author()")
    authors = ol_book["authors"]
    print(f"Authors?\n{authors}")
    db_authors = None

    author_names = []
    for author in authors:
        names = author["name"].split(" ", 2)
        print(names)
        author_names.append(names)

    print(f"List of author names is {author_names}")
    try:
        db_authors = Author.objects.filter(
            first_name=author_names[0][0],
            last_name=author_names[0][1],
        ).first()
    except Author.DoesNotExist:
        print("Whoops, author does not exist.")

    if db_authors is None:

        first = author_names[0][0]
        last = author_names[0][1]
        print(f"No authors by that name, {first} {last}. Creating a new object.")
        db_authors = add_author(first, last)

    print(f"Returning from get_author, result was {db_authors}")
    return db_authors

def add_publisher(name, location):
    print(f"In add_publisher, name is {name} and location is {location}.")

    publisher = Publisher.objects.create(
        name = name,
        location = location,
    )

    return publisher

def get_publisher(ol_book):
    print("\nIn get_publisher()")
    publishers = ol_book["publishers"]
    print(f"Publihsers?\n{publishers}")
    db_publishers = None

    publisher_names = []
    for publisher in publishers:
        name = publisher["name"]
        print(f"Pub name {name}")
        publisher_names.append(name)

    print(f"List of publihser names is {publisher_names}")
    try:
        db_publishers = Publisher.objects.filter(
            name=publisher_names[0]
        ).first()
    except Publisher.DoesNotExist:
        print("Whoops, publisher does not exist.")

    if db_publishers is None:
        db_publishers = add_publisher(publisher_names[0], "")

    print(f"Returning from get_publisher, result was {db_publishers}")
    return db_publishers

def add_genre(name):
    print(f"In add_genre, name is {name}.")

    genre = Genre.objects.create(
        name = name,
    )

    return genre

def get_genre(ol_book):
    print("\nIn get_genre()")
    genres = ol_book["subjects"]
    print(f"Genres?\n{genres}")
    db_genres = None

    genre_names = []
    for genre in genres:
        name = genre["name"]
        print(f"Genre name {name}")
        genre_names.append(name)

    print(f"List of genre names is {genre_names}")
    try:
        db_genres = Genre.objects.filter(
            name=genre_names[0]
        ).first()
    except Genre.DoesNotExist:
        print("Whoops, publisher does not exist.")

    if db_genres is None:
        db_genres = add_genre(genre_names[0])

    print(f"Returning from get_genre, result was {db_genres}")

    return db_genres


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
