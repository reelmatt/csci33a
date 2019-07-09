# Project 1

Web Programming with Python and JavaScript

# Requirements
The only requirement added to the starter list was 'requests', as demoed in
Lecture 4 to call to the Goodreads API.

# Environment Variables
For the application to run, the following environment variables must be set:
    + FLASK_APP=application.py
    + DATABASE_URL=[URI_obtained_from_heroku]
    + GOODREADS_KEY=[key_obtained_from_goodreads]

# Database design
I created my database tables through the CS50 Adminer interface, running raw
SQL commands. The table columns/data types are described below, but a copy of
the commands can be found in the create.sql file.

### books
column name | data type
-----------------------
id          | SERIAL, PRIMARY KEY
isbn        | VARCHAR, UNIQUE, NOT NULL
title       | VARCHAR, NOT NULL
author      | VARCHAR, NOT NULL
year        | INTEGER, NOT NULL

### reviews
column name | data type           | references
------------|---------------------|------------
id          | SERIAL, PRIMARY KEY |
book_id     | INTEGER, NOT NULL   | books
user_id     | INTEGER, NOT NULL   | users
review      | TEXT, NOT NULL      |

### users
column name | data type
-----------------------
id          | SERIAL, PRIMARY KEY
name        | VARCHAR, NOT NULL
username    | VARCHAR, UNIQUE, NOT NULL
password    | VARCHAR, NOT NULL

# Implementation notes
As asked in [this discussion thread](https://us.edstem.org/courses/17/discussion/179),
my project deviates slightly from the specific requirements listed in the
assignment.

+ Search
    + Requirement: "[Logged in users] should be taken to a page where they can
    search for a book... After performing the search, your website should
    display a list of possible matching results..."
    + Implementation: An omni-present search field appears in the navigation bar
    for logged in users. If more than one result is returned from a query, all
    the results are displayed on a page where they can select the one they want.
    In cases where only one result is returned, even in a partial-match case,
    the user is directed to that individual book's information page.
+ Review submission
    + Though not explicitly requested in the requirements, users in my
    implementation can be taken to a page to edit a review they have left on a
    book. Users are still only allowed to leave one review per book.

# Files
+ application.py
+ import.py
+ books.csv
+ static/
    + styles.scss - Custom styles added in addition to Bootstrap; compiled down
      to styles.css using the SASS CLI.
+ templates/
    + 404.html - Used to display a 404 error with page_not_found() method.
    + book.html - Displays an individual book's info and any user reviews.
    + books.html - Displays a list of all books returned for a search with links
        to the individual book page.
    + edit_review.html - Form containing a user's existing review to all them to
        update and re-submit.
    + index.html - Home page for the site. Gives a welcome message and how to
        use the site.
    + layout.html - The main layout template that is extended by all the pages.
    + login.html - Displays form for user to submit login credentials.
    + register.html - Displays form for user to submit info to create a user
        account.
    + includes/
        + nav.html - Universal navigation bar that is included in layout.html.
            When no user is logged in, it displays links to login or create an
            account. When a user is logged in, it displays a search field, and
            a dropdown where the user can logout.
