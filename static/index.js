// Allow socket to be used outside the 'DOMContentLoaded' section
var socket;

document.addEventListener('DOMContentLoaded', () => {
    // Hide any error messages
    safeRemove('channelError');
    safeRemove('messageError');

    // Added Handlebars helper to check equality in if statement
    // Code snippet copied from this Stack Overflow post
    // https://stackoverflow.com/a/51976315
    Handlebars.registerHelper('ifeq', function (a, b, options) {
        if (a == b) { return options.fn(this); }
        return options.inverse(this);
    });

    // Handlebars templates for message and channel
    const message_template = Handlebars.compile(document.querySelector('#message').innerHTML);
    const channel_template = Handlebars.compile(document.querySelector('#channel').innerHTML);

    // If there's a local channel, remove it to start fresh
    let channel = localStorage.removeItem('channel');

    // Connect to websocket
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    /*****************************************************************
     * Add event handlers to elements when connection is established
     *****************************************************************/
    socket.on('connect', () => {
        // Form to create new channel; 'channel error' is emitted if a duplicate
        document.querySelector('#channelNameForm').onsubmit = () => {

            // Check channel name for duplicates
            const channel = document.getElementById('channelName').value;
            socket.emit('create channel', {'name': channel});

            // Clear input field and prevent form from submitting
            clearInput('channelName');
            return false;
        };

        // Form to send messages
        document.querySelector('#messageForm').onsubmit = () => {
            // Get the message text, add user, timestamp, and channel
            const message = constructMessage();

            // If invalid, constructMessage() will return null
            if (message) {
                // Good to go, store in server and clear input
                socket.emit('send message', message);
                clearInput('messageContents');

                // Clear any previous errors
                safeRemove('messageError');
            } else {
                showErrorMessage('messageError', 'Please select a channel to send messages to.');
            }

            return false;
        };
    });


    // If the channel name already exists, display error message
    socket.on('channel error', message => {
        showErrorMessage('channelError', message);
    });


    // A message was sent by some user
    socket.on('receive message', message => {
        // If it does not belong to the current channel, do nothing
        if (message.channel !== localStorage.getItem('channel')) {
            return;
        }

        // Belongs to the current channel, display the message
        addNewContent('messageList', message_template({'message': message, 'localUser': localStorage.getItem('user')}));
    });

    // A message was deleted by its sender
    socket.on('remove message', messageToDelete => {
      // If it does not belong to the current channel, do nothing
      if (messageToDelete.channel !== localStorage.getItem('channel')) {
          return;
      }

      // Get the messages currently displayed on the screen
      const allMessages = document.querySelectorAll('#messageList > li');

      // Search to find the one that matches
      allMessages.forEach(message => {
          const text = message.querySelector('.card-text').innerText;
          const user = message.querySelector('.card-title').innerText;
          const time = message.querySelector('.card-subtitle').innerText;;

          // Check the parts to see if they match
          if (text === messageToDelete.text && user === messageToDelete.user &&
              time === messageToDelete.time) {
              // remove it from the screen and stop looking
              message.remove();
              return;
          }
      });
    });

    // When loading a channel, also load any existing messages
    socket.on('load messages', messages => {
        messages.forEach(message => {
            addNewContent('messageList', message_template({'message': message, 'localUser': localStorage.getItem('user')}));
        });
    });

    // When a valid new channel is entered, add it to the list
    socket.on('list channel', channel => {
      // Clear any previous errors
      safeRemove('channelError');
        addNewContent('channels', channel_template({'channel': channel}));

        let notification = document.querySelector('#channels > p');

        if (notification) {
            notification.style.display = "none";
        }
    });
});

document.addEventListener('click', e => {
    // Only add listeners on buttons
    if (e.target.type === "button") {
        const className = e.target.className;

        // Buttons to change channels
        if (className.search('channel') !== -1) {
            const channel = e.target.name;
            changeChannel(channel);
            return false;
        }
        // Buttons to delete messages
        else if (className.search('deleteMessage') !== -1) {
            const message = e.target.parentNode;
            const messageSender = message.querySelector('.card-title').innerText;
            const user = localStorage.getItem('user');

            // If the messages was sent by the current user, okay to delete
            if (messageSender === user) {
                // Extract the message information
                const thisMessage = {
                  'text': message.querySelector('.card-text').innerText,
                  'user': messageSender,
                  'time': message.querySelector('.card-subtitle').innerText,
                  'channel': localStorage.getItem('channel')
                };

                // Send a notification to server
                socket.emit('delete message', thisMessage);
            }
        }
    }
});

// Add new content (message or channel name) to the appropriate part of the page
function addNewContent(elementId, content) {
    document.getElementById(elementId).innerHTML += content;
};

// Should an error occur, generate the message and display in the appropriate
// section of the page
function showErrorMessage(elementId, message) {
    const error_template = Handlebars.compile(document.querySelector('#errorMessage').innerHTML);
    document.getElementById(elementId).innerHTML = error_template({'message': message});
};

// When the user changes a channel, update localStorage, change the page's
// header, and blank out the messages, to prepare for loading any stored messages
function changeChannel(channel) {
    localStorage.setItem('channel', channel);
    document.getElementById('channelHead').innerText = "#" + channel;
    document.getElementById('messageList').innerHTML = '';
    socket.emit('load channel', channel);
};

// Perform some basic error-checking before creating a message Object to pass
// through to the application.
function constructMessage() {
    // If a channel hasn't been selected, stop message from sending
    if ( ! localStorage.getItem('channel')) {
        return null;
    }

    // Otherwise, get the message contents and timestamp
    const text = document.getElementById('messageContents').value;
    const now = new Date();

    // Create the message Object
    return {
        'text': text,
        'user': localStorage.getItem('user'),
        'time': now.toLocaleString('en-US'),
        'channel': localStorage.getItem('channel')
    };
};

// Helper function to clear the text input field
function clearInput(element) {
    document.getElementById(element).value = '';
};

// Helper function to safely remove an element from the screen, only if such
// an element exists. (Prevents console errors should element *not* exist.)
function safeRemove(elementId) {
  let toRemove = document.getElementById(elementId).firstElementChild;

  if (toRemove) {
    toRemove.remove();
  }
}
