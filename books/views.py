from django.shortcuts import render

# Create your views here.

def book(request, book_id):
    print(f"in book view, id is {book_id}")
    return render(request, "books/book.html")
