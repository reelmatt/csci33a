document.addEventListener('DOMContentLoaded', () => {

    localStorage.removeItem('channel')


    // If no user stored locally, present form for them to register
    if (!localStorage.getItem('user')) {
        console.log("no users...");
        document.querySelector('#enterDisplayName').style.display = "inherit";
    } else {
        console.log(`Any users? ${localStorage.getItem('displayName')}`);
        document.querySelector('#enterDisplayName').style.display = "none";
    }

    document.getElementById('channelError').style.display = "none";
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {
        document.querySelector('#channelNameForm').onsubmit = () => {
            console.log("IN CHANNEL NAME FORMMMMMMMM!");
            // Initialize new request

            const request = new XMLHttpRequest();
            const channel = document.getElementById('channelName').value;
            console.log(`Channel name entered is ${channel}`);
            request.open('POST', '/create');
            console.log("opened request");
            // Callback function for when request completes
            request.onload = () => {
                console.log("in .onload() portion, data is...");
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);

                console.log(data);
                // Update the result div
                if (data.success) {
                    const contents = data.channel;
                    console.log("contents are " + contents);
                    socket.emit('create channel', {'selection': contents});
                    console.log("EMITTED socket");
                    document.getElementById('channelName').value = '';
                }
                else {
                    document.querySelector('#channels').innerHTML = 'There was an error.';
                }
            }

            // Add data to send with request
            const data = new FormData();
            data.append('channel', channel);
            console.log("sending data");
            console.log(data);
            localStorage.setItem('channel', channel);
            // Send request
            request.send(data);
            document.getElementById('channelError').style.display = "none";
            document.getElementById('channelError').innerText = '';

            return false;
        };

        document.querySelector('#messageForm').onsubmit = () => {
                const text = document.getElementById('messageContents').value;
                socket.emit('send message', {'text': text, 'channel': localStorage.getItem('channel')});

                return false;
        };

    });

    socket.on('channel error', message => {
        document.getElementById('channelError').innerText = message;
        document.getElementById('channelError').style.display = "inherit";
    });

    socket.on('receive message', text => {
            console.log("RECEIVING MESSAGE: " + text);
            const li = document.createElement('li');
            li.innerHTML = text;
            document.querySelector("#messageList").append(li);
    });

    socket.on('load messages', data => {
        document.getElementById('messageList').innerHTML = '';
        let list = document.getElementById('messageList');
        console.log(data["messages"]);

        data["messages"].forEach(message => {
            const li = document.createElement('li');
            li.innerHTML = message;
            list.appendChild(li);
        });
    });

    socket.on('channel list', data => {
        console.log("Appending to channel list...");
        console.log(data);
        const li = document.createElement('li');
        const button = document.createElement('button');

        button.setAttribute('class', 'channel');
        button.innerText = data.selection;
        button.onclick = () => {
            localStorage.setItem('channel', data.selection);
            socket.emit('load channel', {'name': data.selection});
        };

        li.appendChild(button);
        console.log(li);
        document.querySelector("#channels").append(li);
    });

    // By default, submit button is disabled
    document.querySelector('#displayNameSubmit').disabled = true;

    // Enable button only if there is text in the input field
    document.querySelector('#displayName').onkeyup = () => {
        if (document.querySelector('#displayName').value.length > 0)
            document.querySelector('#displayNameSubmit').disabled = false;
        else
            document.querySelector('#displayNameSubmit').disabled = true;
    };

    document.querySelector('#displayNameForm').onsubmit = () => {
        console.log("Showing up here...");

        let name = document.querySelector("#displayName").value;

        localStorage.setItem('user', name);

        console.log(`Entered display name of ${name}`);
        document.querySelector('#enterDisplayName').style.visibility = "hidden";


        // Stop form from submitting
        return false;
    };
});
