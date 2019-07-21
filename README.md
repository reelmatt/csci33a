# Project 2

Web Programming with Python and JavaScript

# Personal Touch

For my personal touch, I decided to add one of the recommendations from the
assignment spec: deleting one's own messages. The relevant parts of the code
are the `delete_message()` method in Python as well as the button event
listener and the `socket.on(remove_message)` portions in `index.js`.

For new messages sent, the Handlebars template determines if the message was
sent by the user currently in localStorage. If it is, a delete button ('X'),
is added to the message for that particular user. Should that user click the
button, a socket message is emitted, the message is removed from the
application's memory, and browsers are notified to remove the message from the
display.

# Implementation notes

To allow for unique identification between users (and therefore not allowing
a second user with the same display name to delete one's messages), my
implementation restricts display names to unique.

# Files
+ application.py - main application code
+ requirements.txt - project-provided file; unchanged from initial fork
+ static/
    + styles.scss - Custom styles added in addition to Bootstrap; compiled down
      to styles.css using the SASS CLI.
    + index.js - Main Javascript code to support channels, messages, and more.
        Structured to hide/show things as a single-page application.
    + register.js - A separate helper file to deal with all code related to a
        user entering a display name.
+ templates/
    + index.html - The main layout template. Since this is a single-page
        application, there is only this one main file. Sub-elements are added
        to the page and broken out into 'includes', listed below.
    + includes/
        + channels.html - Display text input to create a new channel, and a
            list of any pre-existing channels for users to switch between.
        + display_name.html - Form for the user to enter a display name for
            identification in the application.
        + message.html - A main portion of the application which displays any
            messages sent to the currently selected channel.
