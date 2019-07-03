import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# For get index in a for..in loop
# https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/
def main():
    f = open("small.csv")
    titleRead = False
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        if titleRead is False:
            print(f"{isbn}")
            titleRead = True
            continue
        print(f"Read record, isbn is {isbn}, title is {title}")
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} by {author}.")
    db.commit()

if __name__ == "__main__":
    main()
