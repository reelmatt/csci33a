import csv
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check table existence in case 'books' has already been made
# https://www.pythonsheets.com/notes/python-sqlalchemy.html
tableCreated = False
ins = inspect(engine)
for _t in ins.get_table_names():
    print(_t)
    if _t == "books":
        tableCreated = True

if tableCreated == False:
    print("Creating table books...")
    db.execute("CREATE TABLE books ("
        "id SERIAL PRIMARY KEY, "
        "isbn VARCHAR UNIQUE NOT NULL, "
        "title VARCHAR NOT NULL, "
        "author VARCHAR, "
        "year INTEGER"
    ")")
    print("...Added table")

# For get index in a for..in loop
# https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/
# https://www.pitt.edu/~naraehan/python3/more_on_for_loops.html
def main():
    f = open("books.csv")
    titleRead = False
    reader = csv.reader(f)

    for isbn, title, author, year in reader:
        if titleRead is False:
            titleRead = True
            print("Starting import, skip the titles")
            print(f"{isbn}")
            continue

        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} by {author}.")
    db.commit()

if __name__ == "__main__":
    main()
