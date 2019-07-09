###############################################################################
# application.py
# Project 1, written by Matthew Thomas
#
# Starter code provided by CSCI s33a team. Many SQL queries were modified
# from examples given in Lecture 3. A few other code bits, new-to-me Python
# constructs are noted, with links, where they appear in the code. See
# README.md for more info.
###############################################################################
import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variables
if not os.getenv("GOODREADS_KEY"):
    raise RuntimeError("GOODREADS_KEY is not set")

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

###############################################################################
# Routes
#   / -- Home page, index.html
#   /api/<isbn> -- Returns, in JSON format, information about given book
#   /books/<book_id> -- Individual book page
#       GET -- Display info about book, and any user reviews
#      POST -- Add a user review to the database
#   /books/<book_id>/edit -- Edit user's review
#       GET -- Display review in <textarea> for user to edit
#      POST -- Submit changes, if any, to database
#   /login
#       GET -- Display form for user to login
#      POST -- Query database to see if user credentials exist
#   /logout -- Remove user from session
#   /register
#       GET -- Display form for user to register an account
#      POST -- Submit user registration, and log the user in
#   /search -- Query database for any (partial) matches for title,
#              author, or isbn
#
###############################################################################

# Home page
@app.route("/")
def index():
    return render_template("index.html", user=get_user())

# API Route
@app.route("/api/<isbn>")
def book_api(isbn):
    # Query database for book, by isbn
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Return error if book does not exist
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422

    # Get COUNT of all reviews for book_id
    id = book["id"]
    reviews = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id = :id", {"id": id}).fetchone()

    # Format response as JSON
    return jsonify({
            "title": book["title"],
            "author": book["author"],
            "year": book["year"],
            "isbn": book["isbn"],
            "review_count": reviews[0]
        })

# Individual book page
@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    # Variable to store error message, None by default
    message = None

    # Obtain user stored in session
    user = get_user()

    # User must be logged in to view book page
    if user is None:
        message = "You must login, or create an account, to view book pages."
        return render_template("index.html", error=message)

    # Check to see if 'user' has any reviews for given 'book_id'
    # Help with long, multi-line strings - https://stackoverflow.com/a/10660443
    user_reviewed = db.execute("SELECT book_id, user_id FROM reviews "
                               "WHERE book_id = :book AND user_id = :user",
                               {"book": book_id, "user": user["id"]}).fetchall()

    # Error if user has already left a review
    # Store message, and proceed with rest of code to load book/review again
    if request.method == "POST" and user_reviewed:
        message = "You've already left a review!"

    # Otherwise, go ahead and INSERT review into database
    elif request.method == "POST":
        cmd = ("INSERT INTO reviews (user_id, book_id, review) "
               "VALUES (:user, :book, :review)")
        args = {
            "user": user["id"],
            "book": book_id,
            "review": request.form.get("review")
        }
        db.execute(cmd, args)
        db.commit()

        # redirect back to book info page (this route)
        return redirect(url_for('book', book_id=book_id))

    # GET request method
    # Retrieve 'book_id' from 'books' table
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()

    # If database does not contain book_id, return 404
    if book is None:
        return page_not_found("That book does not exist!")

    # Load reviews for given book_id; JOIN with users to get user's names
    reviews = db.execute("SELECT review, user_id, name FROM reviews "
                         "JOIN users ON users.id = reviews.user_id "
                         "WHERE book_id = :id", {"id": book_id}).fetchall()

    # Fetch Goodreads info via call to API
    goodreads = get_goodreads_info(book["isbn"])

    # Render page with user (from session), book/reviews (from database),
    # and Goodreads data (via API).
    return render_template("book.html", book=book, reviews=reviews,
                            user_reviewed=user_reviewed, user=user,
                            goodreads=goodreads, error=message)

# Edit user's review
@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_review(book_id):
    # Obtain user stored in session
    user = get_user()

    # POST to submit any update to review
    if request.method == "POST":
        text = request.form.get("review")
        db.execute("UPDATE reviews SET review = :text "
                   "WHERE book_id = :book AND user_id = :user",
                   {"text": text, "book": book_id, "user": user["id"]})
        db.commit()

        # Redirect back to book info page
        return redirect(url_for("book", book_id=book_id))

    # Get user review to return to the page
    user_review = db.execute("SELECT review FROM reviews WHERE book_id = :book "
                             "AND user_id = :user",
                             {"book": book_id, "user": user["id"]}).fetchone()

    return render_template("edit_review.html", review=user_review[0], book_id=book_id, user=user)

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if request.method == "GET" and session.get("user_id") != None:
        return redirect(url_for('index'))
    # No current user, display login form
    elif request.method == "GET":
        return render_template("login.html")

    # User submitted form, check login credentials
    username = request.form.get("username")
    password = request.form.get("password")

    # Call login_user() to query database and check errors
    if login_user(username, password):
        return redirect(url_for('index'))
    else:
        message = "Failed to log in. Try again."
        return render_template("login.html", error=message)

# User logout -- reset session values to None
@app.route("/logout")
def logout():
    session["user_id"] = None
    session["user_name"] = None
    session["user_username"] = None
    return redirect(url_for('index'))

# Register new user
@app.route("/register", methods=["GET", "POST"])
def register():
    # Obtain user stored in session
    user = get_user()

    # If user is already logged in, return home with message
    if request.method == "GET" and user is not None:
        message = "You already are logged in. To create a new account, first logout."
        return render_template("index.html", user=user, error=message)

    # Display registration page
    elif request.method == "GET":
        return render_template("register.html")

    # POSTing to route; create user and add to database
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

    # Check that all parts of the form were submitted
    if not (name and username and password):
        message = "Please fill out all parts of the form to register."
        return render_template('register.html', error=message)

    if user_already_exists(username):
        message = "A user with that username already exists. Please try again."
        return render_template('register.html', error=message)

    # Construct SQL command
    cmd = "INSERT INTO users (name, username, password) VALUES (:name, :username, :password)"
    args = {
        "name": request.form.get("name"),
        "username": request.form.get("username"),
        "password": request.form.get("password")
    }

    # Add user to the database
    db.execute(cmd, args)
    db.commit()

    # And log them in; if error, display message.
    if login_user(username, password):
        return redirect(url_for('index'))
    else:
        return render_template("register.html", error="Creation succeeded, but login failed.")

# Search route - translate "query" into book_id to return book
@app.route("/search", methods=["POST"])
def search():
    # Obtain user stored in session
    user = get_user()

    # Retrieve the user's search query
    query = request.form.get("query")

    # If no search query, return error message
    if not query:
        message = "Please enter a search term."
        return render_template("index.html", error=message, user=user)

    # Construct query to database
    # Force query and db entries to lowercase, and compare using LIKE
    # to retrieve partial matches. Sort by book title.
    cmd = ("SELECT * FROM books WHERE "
            "lower(title) LIKE lower(:query) OR "
            "lower(author) LIKE lower(:query) OR "
            "lower(isbn) LIKE lower(:query) "
            "ORDER BY title")

    # Help with including %-signs in the raw SQL query
    # https://stackoverflow.com/a/18808942
    args = {"query": f'%{query}%'}

    # Perform database search
    books = db.execute(cmd, args).fetchall()

    # See how many results there are
    num_found = len(books)

    # Route the user to all results, specific book, or error
    if num_found > 1:
        return render_template('books.html', books=books, user=user)
    elif num_found is 1:
        return redirect(url_for('book', book_id=books[0]["id"]))
    else:
        return page_not_found("No books found.")

###############################################################################
# Helper methods
#
#  get_goodreads_info() -- Fetch rating data from Goodreads API
#            get_user() -- Store session's user in dictionary for easier access
#          login_user() -- Check credentials and store user in session
#      page_not_found() -- 404 error method
# user_already_exists() -- Check to see if 'username' is already registered
###############################################################################

# Fetch rating data from Goodreads API
def get_goodreads_info(isbn):
    # Load key from environment
    key = os.getenv("GOODREADS_KEY")

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

# Store session's user in dictionary for easier access
def get_user():
    user = {
        "id": session.get("user_id"),
        "name": session.get("user_name"),
        "username": session.get("user_username")
    }

    if user["id"] == None and user["username"] == None:
        return None
    else:
        return user

# Check credentials and store user in session
# Used in /login and /register routes
def login_user(username, password):
    # Search database for user matching username/password pair
    cmd = "SELECT * FROM users WHERE username = :username AND password = :password"
    args = {"username": username, "password": password}
    user = db.execute(cmd, args).fetchone()

    # Return False if no db entry
    if user is None:
        return False;
    # Store the user's info in the session and return True
    else:
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_username"] = user.username
        return True

# 404 error method
def page_not_found(message):
    user = get_user()
    return render_template("404.html", message=message, user=user), 404

# Check to see if 'username' is already registered
def user_already_exists(username):
    user = db.execute("SELECT username FROM users WHERE username = :name",
                      {"name": username}).fetchone()

    # Return True if user exists; False if does not exist
    if user is not None:
        return True
    else:
        return False
