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

    print(f"User logged in is ID: {user}")
    return render_template("index.html", user=user)

# Display all books (will/will not be used?)
# @app.route("/books")
# def books():
#     return render_template("book.html", book="Multiple found")

# Individual book page
@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    if request.method == "POST":
        db.execute("INSERT INTO reviews (user_id, book_id, review) VALUES (:user, :book, :review)", {"user": session.get("user_id"), "book": book_id, "review": request.form.get("review")})
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

    return render_template("book.html", book=book, reviews=reviews)

# Search route - translate "name" into ISBN to return book
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    print(f"The search request was for {query}")

    # Help with including %-signs in the raw SQL query
    # https://stackoverflow.com/a/18808942
    cmd = "SELECT * FROM books WHERE lower(title) LIKE lower(:query) OR author LIKE :query OR isbn LIKE :query"
    books = db.execute(cmd, {"query": f'%{query}%'}).fetchall()
    num_found = len(books)
    print(f"The search returned {num_found} books. Redirecting...")

    if num_found > 1:
        return render_template('books.html', books = books)
    elif num_found is 1:
        return render_template('book.html', book = books[0])
    else:
        return page_not_found("No books found.")
        # return redirect(url_for('error', message="No books found."))
        # return bad_request("No books found....")
        # return render_template('404.html', error="No books found.")

    print(f"The search found {len(books)} books.")
    return redirect(url_for('book', isbn=123))
    # return redirect(url_for('book', isbn=books[0].isbn))

# Ideas on how to use abort() and write error handler
# http://flask.pocoo.org/docs/1.0/patterns/errorpages/
@app.errorhandler(404)
def page_not_found(message):
    return render_template("404.html", error=message), 404

@app.route("/404")
def error(message):
    return render_template("404.html", error=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    cmd = "INSERT INTO users (username, password) VALUES (:username, :password)"

    # if request.form.get("name"):
    #     print("")
    # elif request.form.get("username"):
    #
    # elif request.form.get("password"):
    #
    # else:
    db.execute(cmd, {
        # "name": request.form.get("name"),
        "username": request.form.get("username"),
        "password": request.form.get("password")
    })
    db.commit()
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect(url_for('index'))

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")


    username = request.form.get("username")
    password = request.form.get("password")
    print(f"Login route. Checking database for user {username}")
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()


    if user is None:
        return render_template("login.html", error="Failed to log in. Try again.")
    else:
        print(f"User id is {user.id} and name is {user.username}")
        session["user_id"] = user.id
        return redirect(url_for('index'))
