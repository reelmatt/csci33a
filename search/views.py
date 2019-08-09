import os
import requests
from django.apps import apps
from django.shortcuts import render
from django.db.models import Q
from library.models import Book
# Peform a search
def search(request):
    if not request.GET:
        return render(request, "search/search.html")

    query = request.GET.get("query")
    option = request.GET.get("queryOptions")

    if option is None:
        option = "title"

    ol_query = f"{option}={query}"
    result = search_openlibrary(ol_query)

    title = Q(title=query)
    authors = Q(authors__first_name=query)
    db_books = Book.objects.filter(
        title | authors
    ).all()

    context = {
        "query": f"{option}={query}",
        "safeQuery": "-".join(query.split(" ")),
        "books": result,
        "db_books": db_books,
    }
    return render(request, "search/books.html", context)

def work(request, book_query, index):
    safe_query = "%20".join(book_query.split(" "))
    result = search_openlibrary(safe_query)

    selected = result[index]
    work = get_openlibrary_works(selected["key"])

    editions = get_openlibrary_editions(selected['edition_key'])

    context = {
        "work": work,
        "num_editions": len(selected['edition_key']),
        "editions": editions,
    }
    return render(request, "search/work.html", context)

# Search
# https://openlibrary.org/dev/docs/api/search
def search_openlibrary(query):
    url = f"http://openlibrary.org/search.json?{query}"
    res = requests.get(url)

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()
    return data["docs"]

# Create a list of OLIDs to query Open Library API for
# https://openlibrary.org/dev/docs/api/books
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

# Get Works - append '.json' to end of URL to get results
# https://openlibrary.org/developers/api
def get_openlibrary_works(work_id):
    base_url = f"http://openlibrary.org/{work_id}.json"
    res = requests.get(base_url)

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()
    return data
