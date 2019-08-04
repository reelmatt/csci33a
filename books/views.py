import os
import requests
from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render
from library.models import Edition, Book, Library, Author, Publisher, Genre


# Create your views here.
def acquire(request, book_id):
    # authors = Author.objects.filter()
    # publisher = Publisher.Objects
    # genre = Genre.objects
    # book = Book.objects.create(
    #     title =
    #     publisher =
    #     genre =
    # )
    #
    # book.authors.set(authors)

    print(f"\n\nIN ACQUIRE, id is {book_id}")
    return HttpResponseRedirect(reverse("book", kwargs={"book_id": book_id}))


def book(request, book_id):
    print(f"in book view, id is {book_id}")

    result = search_openlibrary(book_id)

    # Access a dictionary item by index
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    key = list(result.keys())[0]




    context = {
        "book": result[key]
    }
    return render(request, "books/book.html", context)


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
