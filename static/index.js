// Allow socket to be used outside the 'DOMContentLoaded' section
var socket;

document.addEventListener('DOMContentLoaded', () => {

    const message_template = Handlebars.compile(document.querySelector('#message').innerHTML);
    const channel_template = Handlebars.compile(document.querySelector('#channel').innerHTML);

    let channel = localStorage.removeItem('channel');
    // console.log("Do we have a local channel?");
    // console.log(channel);

    document.getElementById('channelError').style.display = "none";
    document.getElementById('messageError').style.display = "none";

    // Connect to websocket
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    /*****************************************************************
     * Add event handlers to elements when connection is established
     *****************************************************************/
    socket.on('connect', () => {
        // Form to create new channel; 'channel error' is emitted if a duplicate
        document.querySelector('#channelNameForm').onsubmit = () => {
            // Clear any previous errors
            document.getElementById('channelError').style.display = "none";

            // Check channel name for duplicates
            const channel = document.getElementById('channelName').value;
            socket.emit('create channel', {'name': channel});

            // Clear input field and prevent form from submitting
            clearInput('channelName');
            return false;
        };

        // Form to send messages
        document.querySelector('#messageForm').onsubmit = () => {
            // Clear any previous errors
            document.getElementById('messageError').style.display = "none";

            // Get the message, add user/timestamp, and add to Flask memory
            const message = constructMessage();

            // Clear input field and prevent form from submitting
            if (message) {
                socket.emit('send message', message);
                clearInput('messageContents');
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
        // If it does not belong to the current channel, do not add it
        if (message.channel !== localStorage.getItem('channel')) {
            return;
        }

        // Belongs to the current channel, display the message
        addNewContent('messageList', message_template({'message': message}));
    });

    socket.on('remove message', messageToDelete => {
      // If it does not belong to the current channel, do not add it
      if (messageToDelete.channel !== localStorage.getItem('channel')) {
          return;
      }

      console.log("REMOVE THE MESSAGE");

      const allMessages = document.querySelectorAll('#messageList > li');
      // console.log(allMessages[0]);

      allMessages.forEach(message => {
          console.log(message);
            const text = message.querySelector('.card-text').innerText;
            const user = message.querySelector('.card-title').innerText;
            const time = message.querySelector('.card-subtitle').innerText;;

            if (text === messageToDelete.text && user === messageToDelete.user && time === messageToDelete.time) {
                console.log("MESSAGES MATCH!!!!");
                message.remove();
                return;
            } else {
              console.log("NO MATCH!");
            }
      });
    });

    // When loading a channel, also load any existing messages
    socket.on('load messages', messages => {
        messages.forEach(message => {
            addNewContent('messageList', message_template({'message': message}));
        });
    });

    // When a valid new channel is entered, add it to the list
    socket.on('list channel', channel => {
        addNewContent('channels', channel_template({'channel': channel}));

        let notification = document.querySelector('#channels > p');

        if (notification) {
            notification.style.display = "none";
        }
    });
});

document.addEventListener('click', e => {
    // console.log("EVENT LISTENER");
    console.log(e.target.className);
    // console.log(e.target [.class, .tagName, .name, .type]);
    if (e.target.type === "button") {
        const className = e.target.className;
        if (className.search('channel') !== -1) {
            console.log("SUCCESS!!!!");
            console.log(className.search('channel'));
            const channel = e.target.name;
            // socket.emit('load channel', channel);
            changeChannel(channel);
            return false;
            // document.getElementById('channelHead').innerText = "#" + e.target.name;
        } else if (className.search('deleteMessage') !== -1) {
            console.log("DELETE MESSAGE");
            const message = e.target.parentNode;
            console.log(message);
            const messageSender = message.querySelector('.card-title').innerText;
            console.log("SENDER: ");
            console.log(messageSender);
            const user = localStorage.getItem('user');


            if (messageSender === user) {
                console.log("ALLOWED TO DELETE. EMIT MESSAGE");

                const thisMessage = {
                  'text': message.querySelector('.card-text').innerText,
                  'user': messageSender,
                  'time': message.querySelector('.card-subtitle').innerText,
                  'channel': localStorage.getItem('channel')
                };

                console.log(thisMessage);
                socket.emit('delete message', thisMessage);
            }
        }

    }

});

function addNewContent(elementId, content) {
    document.getElementById(elementId).innerHTML += content;
};

function showErrorMessage(elementId, message) {
    document.getElementById(elementId).innerText = message;
    document.getElementById(elementId).style.display = "inherit";
};

function changeChannel(channel) {
    localStorage.setItem('channel', channel);
    document.getElementById('channelHead').innerText = "#" + channel;
    document.getElementById('messageList').innerHTML = '';
    socket.emit('load channel', channel);
};

function constructMessage() {
    console.log("IN constructMessage()");

    if ( ! localStorage.getItem('channel')) {
        return null;
    }
    const text = document.getElementById('messageContents').value;
    const now = new Date();

    return {
        'text': text,
        'user': localStorage.getItem('user'),
        'time': now.toLocaleString('en-US'),
        'channel': localStorage.getItem('channel')
    };
};

function clearInput(element) {
    document.getElementById(element).value = '';
};
