# final-project

# Users
Tutorials/documentation:
https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
https://wsvincent.com/django-custom-user-model-tutorial/

Login/Logout/Register and custom forms:
https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
https://wsvincent.com/django-user-authentication-tutorial-signup/


Forms:
https://docs.djangoproject.com/en/2.2/topics/forms/modelforms/#django.forms.ModelForm

# Database design

The basic components of the app are users, which Django helpfully provides a
good place to start, and libraries. A more complicated design/app might have
a ManyToMany relationship between users and libraries, such that a user can
belong to multiple libraries (either of their own, or those of friends) and
contain a sharing component. To keep things simple, at least for this final
project, libraries are implemented as a OneToOneField with users. Each user
can have only one library, and therefore, each library can have only one user.

In a library can exist multiple Editions. An Edition is an instance of a Book,
which customized information for the given user. Say a Book is listed with a
category of Science Fiction but the user classifies it as Fantasy. Another
example is page count or minutes, which could vary depending on physical,
digital ebook, or audiobook that user is reading.

+ User (custom model)
    + No changes/additions
    + Goodreads User ID (?) - for "BEST" outcome and sharing data back to Goodreads
+ Library (a list of Editions in a user's library, with further customizations if needed)
    + user_id
        + OneToOneField (Each library has only one user - each user has only one library)
    + edition_id
        + ManyToManyField (Many books can belong to many libraries)
    + category (if different from edition value)
    + num_pages (if different from edition value)
    + num_minutes (if different from edition value)
+ Book (basic, un-changeable book info)
    + Title
        + CharField
    + Author_id
        + ManyToManyField (Many books can belong to many authors - some have multiple)
    + Publisher_id
        + ForeignKey (Many books can belong to one publisher)
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
    + category_id
    + num_pages (for non-audiobooks)
        + Int
    + num_minutes (only for audiobooks)
        + Int
+ Author
    + First name
        + CharField
    + Last name
        + CharField
+ Category
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
