import os

from flask import Flask, session, render_template, request, redirect, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Home page
@app.route("/")
def index():
    user = session.get("user_id")
    print(f"INDEX route. User id is {user}")
    return render_template("index.html", user=get_user())

# Display all books (will/will not be used?)
# @app.route("/books")
# def books():
#     return render_template("book.html", book="Multiple found")

# Individual book page
@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    user = get_user()
    print(user)

    message = None
    user_reviewed = db.execute("SELECT (book_id, user_id) FROM reviews WHERE book_id = :book AND user_id = :user", {"book": book_id, "user": user["id"]}).fetchall()

    print(f"user_reviewed is {user_reviewed}")
    if request.method == "POST" and user_reviewed:
        message = "You've already left a review!"
    elif request.method == "POST":
        cmd = "INSERT INTO reviews (user_id, book_id, review) VALUES (:user, :book, :review)"
        args = {
            "user": user["id"],
            "book": book_id,
            "review": request.form.get("review")
        }
        db.execute(cmd, args)
        db.commit()
        #log review to database
        return redirect(url_for('book', book_id=book_id))

    print(f"The isbn is {book_id}")
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()

    if book is None:
        print("Book does not exist!")
    else:
        print(book)
        print(f"There are {len(reviews)} reviews.")

    return render_template("book.html", book=book, reviews=reviews, user_reviewed=user_reviewed, user=user, error=message)


# Individual book page
@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_review(book_id):
    user = get_user()
    if request.method == "POST":
        db.execute("UPDATE reviews SET review = :text WHERE book_id = :book AND user_id = :user", {"text": request.form.get("review"), "book": book_id, "user": user["id"]})
        db.commit()
        return redirect(url_for("book", book_id=book_id))

    user_review = db.execute("SELECT review FROM reviews WHERE book_id = :book AND user_id = :user", {"book": book_id, "user": user["id"]}).fetchone()

    print(user_review[0])
    return render_template("edit_review.html", review=user_review[0], book_id=book_id, user=user)

# Search route - translate "name" into ISBN to return book
@app.route("/search", methods=["POST"])
def search():
    # Retrieve the user's search query
    query = request.form.get("query")

    # Help with long, multi-line string
    # https://stackoverflow.com/a/10660443
    cmd = ("SELECT * FROM books WHERE "
            "lower(title) LIKE lower(:query) OR "
            "lower(author) LIKE lower(:query) OR "
            "lower(isbn) LIKE lower(:query)")

    # Help with including %-signs in the raw SQL query
    # https://stackoverflow.com/a/18808942
    args = {"query": f'%{query}%'}

    # Query database for search term
    books = db.execute(cmd, args).fetchall()
    num_found = len(books)

    # Get current session's user for page template
    user = get_user()

    # Route the user to all results, specific book, or error
    if num_found > 1:
        books.sort(key=get_title)
        return render_template('books.html', books=books, user=user)
    elif num_found is 1:
        return render_template('book.html', book=books[0], user=user)
    else:
        return page_not_found("No books found.")


@app.route("/404")
def page_not_found(message):
    user = get_user()
    return render_template("404.html", error=message, user=user), 404

# Register new user
@app.route("/register", methods=["GET", "POST"])
def register():
    user = session.get("user_id")

    if request.method == "GET":
        return render_template("register.html", user=session.get("user_id"))

    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

    if not (name and username and password):
        message = "Please fill out all parts of the form to register."
        return render_template('register.html', error=message)

    cmd = "INSERT INTO users (username, password, name) VALUES (:username, :password, :name)"
    args = {
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "name": request.form.get("name")
    }

    db.execute(cmd, args)
    db.commit()

    if login_user(username, password):
        return redirect(url_for('index'))
    else:
        return render_template("register.html", error="Creation but login fail.")

#User logout
@app.route("/logout")
def logout():
    session["user_id"] = None
    session["user_name"] = None
    return redirect(url_for('index'))

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

# Helper methods to extract common info
def get_user():
    user = {
        "id": session.get("user_id"),
        "name": session.get("user_name")
    }
    print(user)
    if user.get("id") == None and user.get("name") == None:
        return None
    else:
        return user

def get_title(item):
    return item["title"]

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
        session["user_name"] = user.username
        return True
