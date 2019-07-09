###############################################################################
# import.py
# Project 1, written by Matthew Thomas
#
# Starter code provided by CSCI s33a team, in import.py from Lecture 3. Most of
# the code has been unmodified, save for differences in table column names seen
# in the for loop.
###############################################################################
import csv
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Read 'books.csv' into the 'books' database table
def main():
    # Open csv file
    f = open("books.csv")
    reader = csv.reader(f)

    # Keep track of books added, and if title row has been read
    titleRead = False
    books_added = 0

    # Loop through each entry in books.csv and add to database
    for isbn, title, author, year in reader:
        # Skip the first row with header names
        if titleRead is False:
            titleRead = True
            print("Starting books.csv import...")
            continue

        db.execute("INSERT INTO books (isbn, title, author, year) "
                   "VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        books_added += 1

    db.commit()

    # Log the results
    print(f"Finished! There were {books_added} books added.")

if __name__ == "__main__":
    main()
