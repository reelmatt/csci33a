import os
import requests

from django.shortcuts import render




def search(request):
    if not request.GET:
        return render(request, "search/search.html")


    query = request.GET.get("query")
    option = request.GET.get("queryOptions")
    print(f"\n\nTHE SEARCH QUERY - {query}, options, {option}")

    result = search_openlibrary(query, option)
    # print(result)
    context = {
        "query": f"{option}: {query}",
        "books": result,
    }
    return render(request, "search/books.html", context)


def search_goodreads(isbn):

    key = os.getenv("GOODREADS_KEY")

    print(f"searching... key is {key}")
    # Base URL to query
    # Documentation @ https://www.goodreads.com/api/index#book.review_counts
    url = "https://www.goodreads.com/book/review_counts.json"
    res = requests.get(url, params={"isbns": isbn, "key": key})

    # Check response is OK
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()
    ratings_count = data["books"][0]["work_ratings_count"]
    average = data["books"][0]["average_rating"]

    return {"count": ratings_count, "rating": average}


def search_openlibrary(query, option):
    url = "http://openlibrary.org/search.json?"
    res = requests.get(url, params={option: query})

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # Parse response and extract info
    data = res.json()

    return data["docs"]
