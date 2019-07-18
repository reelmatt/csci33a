document.addEventListener('DOMContentLoaded', () => {

    localStorage.removeItem('channel')
    const message_template = Handlebars.compile(document.querySelector('#message').innerHTML);

    // If no user stored locally, present form for them to register
    if (!localStorage.getItem('user')) {
        console.log("no users...");
        document.querySelector('#enterDisplayName').style.display = "inherit";

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
            document.querySelector('#enterDisplayName').remove();


            // Stop form from submitting
            return false;
        };
    } else {
        console.log(`Any users? ${localStorage.getItem('displayName')}`);
        document.querySelector('#enterDisplayName').remove();
    }

    document.getElementById('channelError').style.display = "none";


    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {
        document.querySelector('#channelNameForm').onsubmit = () => {
            const channel = document.getElementById('channelName').value;

            socket.emit('create channel', {'name': channel});

            document.getElementById('channelError').style.display = "none";
            document.getElementById('channelError').innerText = '';
            document.getElementById('channelName').value = '';
            return false;
        };

        document.querySelector('#messageForm').onsubmit = () => {
                const text = document.getElementById('messageContents').value;
                const now = new Date();
                socket.emit('send message', {
                    'text': text,
                    'user': localStorage.getItem('user'),
                    'time': now.toLocaleString('en-US', {timeZone: 'EST'}),
                    'channel': localStorage.getItem('channel')
                });
                document.getElementById('messageContents').value = '';
                return false;
        };

        // Each button should emit a "submit vote" event
        document.querySelectorAll('button.channel').forEach(button => {
            console.log("button name is " + button.name);
            button.onclick = () => {
                localStorage.setItem('channel', button.name);
                document.getElementById('channelHead').innerText = button.name;
                socket.emit('load channel', button.name);
            };
        });
    });

    socket.on('channel error', message => {
        document.getElementById('channelError').innerText = message;
        document.getElementById('channelError').style.display = "inherit";
    });

    socket.on('receive message', message => {
            console.log("RECEIVING MESSAGE: ");
            console.log(message);
            if (message.channel !== localStorage.getItem('channel')) {
                return;
            }
            const temp = message_template({'message': message});
            console.log(temp);
            // const li = document.createElement('li');
            // li.innerHTML = message.text + ' sent by ' + message.user + ' at ' + message.time;
            document.querySelector("#messageList").innerHTML += temp;
    });

    socket.on('load messages', data => {
        console.log("Loading messages....");


        // localStorage.setItem('channel', data.channel);
        document.getElementById('messageList').innerHTML = '';
        let list = document.getElementById('messageList');
        console.log(data["messages"]);
        if (data["messages"]) {
            data["messages"].forEach(message => {
                const temp = message_template({'message': data});
                console.log(temp);
                // const li = document.createElement('li');
                // li.innerHTML = message.text + ' sent by ' + message.user + ' at ' + message.time;
                list.innerHTML += temp;
            });
        }

    });

    socket.on('channel list', data => {
        console.log("Appending to channel list...");
        console.log(data.channel);
        document.getElementById('channelHead').innerText = data.channel;
        localStorage.setItem('channel', data.channel);
        const li = document.createElement('li');
        const button = document.createElement('button');
        document.getElementById('messageList').innerHTML = '';
        button.setAttribute('class', 'channel');
        button.innerText = data.channel;
        button.onclick = () => {
            console.log("ON CLICK TRIGGER!!");
            document.getElementById('channelHead').innerHTML = data.channel;
            localStorage.setItem('channel', data.channel);
            socket.emit('load channel', data.channel);
        };

        li.appendChild(button);
        console.log(li);
        document.querySelector("#channels").append(li);
    });




});
