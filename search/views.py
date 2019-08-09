import os
import requests

from django.shortcuts import render


def search(request):
    if not request.GET:
        return render(request, "search/search.html")

    query = request.GET.get("query")
    option = request.GET.get("queryOptions")

    result = search_openlibrary(query, option)

    safe_query = "-".join(query.split(" "))

    context = {
        "query": f"{option}={query}",
        "safeQuery": safe_query,
        "books": result,
    }
    return render(request, "search/books.html", context)



def work(request, book_query, index):
    print(f"RETRIEVING A BOOK: {book_query} with index {index}.")
    safe_query = "%20".join(book_query.split(" "))
    result = search_openlibrary_indvididual(safe_query, index)

    selected = result[index]


    work = get_openlibrary_works(selected["key"])

    # print(work)
    editions = get_openlibrary_editions(selected['edition_key'])

    context = {
        "work": work,
        "num_editions": len(selected['edition_key']),
        "editions": editions,
        # "edition": edition
    }
    return render(request, "search/work.html", context)


def search_openlibrary(query, option):
    url = "http://openlibrary.org/search.json?"
    res = requests.get(url, params={option: query})

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    return data["docs"]



def search_openlibrary_indvididual(query, index):
    url = f"http://openlibrary.org/search.json?{query}"
    res = requests.get(url)

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    return data["docs"]

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


    print(f"What did we get for keys? {key}");

    res = requests.get(url, params={
        "bibkeys": key,
        "format": "json",
        "jscmd": "data",
    })


    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    # print(data)
    return data

def get_openlibrary_book(book_id):
    url = f"https://openlibrary.org/books/{book_id}.json"

    res = requests.get(url)


    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    return data["title"]

def get_openlibrary_works(work_id):


    base_url = f"http://openlibrary.org/{work_id}.json"

    # url = "http://openlibrary.org/api/books?"
    # key = f"OLID:{book_id}"

    # res = requests.get(url, params={
    #     "bibkeys": key,
    #     "format": "json",
    #     "jscmd": "data",
    # })
    res = requests.get(base_url)

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    return data
