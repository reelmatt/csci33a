import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
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
    return render_template("index.html")

# Display all books (will/will not be used?)
@app.route("/books")
def books():
    return render_template("book.html")

# Individual book page
@app.route("/books/<string:isbn>")
def book(isbn):
    print(f"The isbn is {isbn}")
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    # books = db.execute("SELECT * FROM books LIMIT 5").fetchall()

    if book is None:
        print("Book does not exist!")
    else:
        print(book)


    return render_template("book.html", book=book)

# Search route - translate "name" into ISBN to return book
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    isbn = 123
    return redirect(url_for('book', isbn=isbn))

# User login
@app.route("/login")
def login():
    return render_template("index.html")
