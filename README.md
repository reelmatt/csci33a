# final-project

Web Programming with Python and JavaScript

# Requirements

+ Web application utilizes *Python* and *SQL*, via Django models and Django's ORM.
+ Web application is mobile responsive, using Bootstrap CSS styles and layout to adjust display based on screen size.
+ README and requirements.txt - see here!

# Project accomplishments

As mentioned in my initial proposal, the basic idea for my site was a modified
version of Goodreads; the Book Survey app is meant to be a pseudo-library that tracks multiple-stages of the book-ownership life. The goals I set out in the proposal were:
  + Good:
    + Organize books (add to individual library)
      + This is the feature that took the most time to develop, due to the Open Library
        API. Going to the 'search' route and performing a query seems like it
        returns promising results, but each 'work' (as Open Library calls the
        result) contains many different 'books', or editions, that can be
        selected from. My app shows the listing, and then an individual book
        page to list the different options, from which you can usually pick the one
        you want based on the publisher info.
    + Customize "default" information pulled in from 3rd-party source
      + If you find a book you like, and you click the 'Acquire' button, the app
        displays a form with the information it will store in your library.
        Most fields will be editable, so you can change how a book is
        classified; helpful if you don't like the genre associated with the book. This is even more of a necessary feature using the Open Library
        API which will store genres like "Elves" with *The Lord of the Rings*.
    + More granular report of statistics
      + This is a partial success in my book. The reporting isn't as
        sophisticated as I imagined at the beginning, but it does lay the
        groundwork to continue to add and customize going forward.
  + Better:
    + Categorize books by state (reading, to-be-read, did-not-finish)
      + Like the statistics, I can imagine this feature being more
        fully-fledged in the future. You can categorize books in different
        states by assigning a status to them (accessed via 'Your Library').
        You can get a grouping effect essentially by requesting stats for a
        given 'Action' (Reading, TBR, DNF, etc.) and then specifying a long
        enough report window.
    + Add unpublished works (like ARCs)
      + In addition to search, which will query the Open Library database,
        users can also add a book manually, which could allow duplicates as
        currently implemented (there is no check to see if the ISBN is a
        duplicate, for example), is intended to be used for adding unpublished
        works, or results that would not otherwise show up in the Open Library
        database (like Advanced Reader Copies, and others).
  + Best:
    + Share information/books logged in Book Survey on Goodreads
      + I was focused more on the Good and Better categories, so ended up running
      out of time to try and implement this feature. As noted in my initial proposal,
      there seemed to be a bug with user/profile IDs in Goodreads, which may complicate the creation of this feature  even further.

Many parts of this project proved more difficult and more in-depth than I
originally anticipated. Overall, I feel positive about the end result; not
necessarily with how some of the specific pages look or function, but with
the setup and structure of how I went about designing the site.

Two areas this is apparent in are the database design (more info below) and
taking a structured approach during development. For the database design I
followed a process similar to project 3, where I put in time and effort to plan
before writing the code. A few changes and additions needed to be made along the way, but the thinking I did for the database really helped drive structuring development,
and I think it sets a strong foundation for further development work.

I separated major features out into separate branches to structure adding new
pieces, instead of trying to build everything at once. That did help get me up
and running a whole lot faster, which helped to iterate faster as well.

When it came to fine tuning the details, I'm less pleased compared to
previous projects. A lot of development went into re-writing the
search/addition feature, which proved difficult. Figuring out differences
between ISBNs, editions, books, publishers, authors, and others was much more
challenging than originally anticipated.

# Files
+ books/
  + templates/
    + acquire.html - Page to customize book info for own library
    + add.html - Add a book not found in search/unpublished
    + book.html - Displays book information
  + urls.py - Paths used by the application
  + views.py - Code dealing with individual books and adding to
    a user's library.
+ bookSurvey/ - Project code
  + settings.py - Added lines for login/logout redirect,
  root-level templates and static files, and including
  project applications.
  + urls.py - Paths used by the project
+ library/
  + migrations/ - All generated using `python3 manage.py makemigrations`
  + templates/
    + edition.html - Displays book info, including customizations entered by a particular user.
    + library.html - Displays a list of all books added to a user's library.
    + stats.html - Displays stats about user's actions, with form to customize stats.
  + admin.py - Added Library models
  + models.py - All database models used for the app.
    + Includes Library, Book, Edition, UserEdition, Author, Format, Genre, Publisher, Event, and Action. See *Database design* below, and comments, for more info.
  + urls.py - Paths used by the application
  + views.py - Code dealing with
+ search/
  + templates/
    + books.html - Displays a list of search results.
    + search.html - Displays form for user to perform search.
    + work.html - Displays 'work' information (like cover and description), with links to a specific book edition.
  + urls.py - Paths used by the application
  + views.py - Code dealing with
+ static/
  + styles (SCSS and CSS)
+ templates/
  + base.html - Main template to extend for individual pages
  + index.html - Main homepage (similar/same to project 1)
  + nav.html - Navigation bar, included in `base.html`
+ users/
  + migrations/ - All generated using `python3 manage.py makemigrations`
  + templates/
    + login.html - Login page
    + register.html - Page to create new user
  + models.py - Custom user model, no changes actually made.
  Created per Django documentation which suggests to do so, in
  case it is needed down-the-road. See 'Users' below for links.
  + urls.py - Paths used by the application
  + views.py - Code dealing with
+ db.sqlite3 - Database, with some users, books, and more.
+ manage.py - Part of Django project.
+ README.md - This file.
+ requirements.txt - App requirements. `python-dotenv` was not
  actually used - it was meant for potential Goodreads
  integration (Open Library does not have any API keys). Left
  in the requirements and is set up to be used in the
  application.


# Users

Tutorials/documentation:
https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
https://wsvincent.com/django-custom-user-model-tutorial/

Login/Logout/Register and custom forms:
https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
https://wsvincent.com/django-user-authentication-tutorial-signup/

Forms (ended up not being used):
https://docs.djangoproject.com/en/2.2/topics/forms/modelforms/#django.forms.ModelForm

# Database design

The basic components of the app are users, which Django helpfully provides a
good place to start, and libraries. A more complicated design/app might have
a ManyToMany relationship between users and libraries, such that a user can
belong to multiple libraries (either of their own, or those of friends) and
contain a sharing component. To keep things simple, at least for this final
project, libraries are implemented as a OneToOneField with users. Each user
can have only one library, and therefore, each library can have only one user.

One Library can have multiple UserEditions. A UserEdition references an Edition,
which in turn references a Book. A Book stores basic, unchanging information like
the title, author, and publisher. An Edition stores information that can change,
or is otherwise more detailed like number of pages, book identifiers (ISBN, etc.).
A UserEdition stores user-specified information that might differ from what the
Open Library database prescribes. For example, say a Book is listed with a category
of Science Fiction but the user classifies the book as Fantasy. That change is
stored in the UserEdition model.

+ User (custom model)
    + No changes/additions
    + Goodreads User ID (?) - for "BEST" outcome and sharing data back to Goodreads
+ Library (a list of Editions in a user's library, with further customizations if needed)
    + user_id
        + OneToOneField (Each library has only one user - each user has only one library)
    + edition_id
        + ManyToManyField (Many books can belong to many libraries)
+ Book (basic, un-changeable book info)
    + Title
        + CharField
    + Author_id
        + ManyToManyField (Many books can belong to many authors - some have multiple)
    + Publisher_id
        + ForeignKey (Many books can belong to one publisher)
    + genre_id
+ Edition (more detailed book info that can vary)
    + book_id
        + ForeignKey (A book can have many editions)
    + ISBN - 10
        + CharField (max_length = 10) - can have leading 0s and 'X's, so need a CharField
    + ISBN - 13
        + CharField (max_length = 13) - can have leading 0s and 'X's, so need a CharField
    + Goodreads_id
        + CharField (max_length = ?) - seem to be integers, but since most other IDs are CharFields, should keep ID fields consistent
    + Open library_id
        + CharField (max_length = 11) - ex. "OL22853304M"
    + Publication year
        + Int
    + format
        + ForeignKey (Many books can belong to one type of format)
    + num_pages (for non-audiobooks)
        + Int
    + num_minutes (only for audiobooks)
        + Int
+ UserEdition
    + edition_id (ForeignKey)
    + genre (if different from edition value)
    + num_pages (if different from edition value)
    + num_minutes (if different from edition value)
+ Author
    + First name
        + CharField
    + Last name
        + CharField
+ Genre
    + Name (e.g. Science Fiction, Historical, Biography, etc.)
        + CharField
+ Publisher
    + Name
        + CharField
    + Location
        + CharField
+ Format
    + Type
        + CharField
        + Options = ARC, ebook, paperback, hardcover, graphic novel, mass market, audio
+ Events (historical log of user's actions with a given Edition)
    + user_id
    + edition_id
    + action_id
    + pages_read
    + minutes_listened
    + finished?
    + created_date
    + modified_date
+ Action
    + type (acquired, read, finished, DNF, TBR)
