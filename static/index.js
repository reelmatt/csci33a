document.addEventListener('DOMContentLoaded', () => {

    const message_template = Handlebars.compile(document.querySelector('#message').innerHTML);
    const channel_template = Handlebars.compile(document.querySelector('#channel').innerHTML);

    let channel = localStorage.getItem('channel');



    document.getElementById('channelError').style.display = "none";

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


    /*******************************
     * Create and switch channels
     *******************************/
    // When connected, configure buttons
    socket.on('connect', () => {
        if (channel) {
            socket.emit('load channel', channel);
        }
        document.querySelector('#channelNameForm').onsubmit = () => {
            const channel = document.getElementById('channelName').value;

            socket.emit('create channel', {'name': channel});

            document.getElementById('channelError').style.display = "none";

            clearInput('channelName');
            return false;
        };

        document.querySelector('#messageForm').onsubmit = () => {
                const text = document.getElementById('messageContents').value;

                socket.emit('send message', constructMessage(text));
                clearInput('messageContents');
                return false;
        };

        // For any channels previously added, make button change display
        document.querySelectorAll('button.channel').forEach(button => {
            console.log("button name is " + button.name);
            // button.onclick = loadChannel(button.name);
           button.onclick = () => {
                console.log("OTHER onclick");
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
            document.querySelector("#messageList").innerHTML += message_template({'message': message});
    });

    socket.on('load messages', data => {
        console.log("Loading messages....");
        document.getElementById('channelHead').innerText = localStorage.getItem('channel');
        document.getElementById('messageList').innerHTML = '';
        let list = document.getElementById('messageList');
        console.log(data["messages"]);
        if (data["messages"]) {
            data["messages"].forEach(message => {
                list.innerHTML += message_template({'message': message});
            });
        }

    });

    socket.on('channel list', channel => {
/*
        document.getElementById('channelHead').innerText = channel;
        localStorage.setItem('channel', channel);

        // let list = document.getElementById('channels');
        //
        // const li = document.createElement('li');
        document.getElementById('channels').innerHTML += channel_template({'channel': channel});
        // const button = channel_template({'channel': channel});
        // console.log(button);
        // const button = document.createElement('button');
        // document.getElementById('messageList').innerHTML = '';
        // button.setAttribute('class', 'channel');
        // button.innerText = channel;
        let button = document.querySelector(`button[name="${channel}"]`);
        console.log(button);


        button.onclick = () => {
            console.log("ON CLICK TRIGGER!!");
            document.getElementById('channelHead').innerHTML = channel;
            localStorage.setItem('channel', channel);
            socket.emit('load channel', channel);
        };
        // li.innerText = button;
        // li.appendChild(button);
        // console.log(li);
        // list.innerHTML += button;
        // document.querySelector("#channels").append(li);
    });
*/

        document.getElementById('channelHead').innerText = channel;
        localStorage.setItem('channel', channel);
        const li = document.createElement('li');
        const button = document.createElement('button');
        document.getElementById('messageList').innerHTML = '';
        button.setAttribute('class', 'channel');
        button.innerText = channel;
        // button.onclick = loadChannel(channel);
        button.onclick = () => {
            console.log("ON CLICK TRIGGER!!");
            document.getElementById('channelHead').innerHTML = channel;
            localStorage.setItem('channel', channel);
            socket.emit('load channel', channel);
        };

        li.appendChild(button);
        console.log(li);
        document.querySelector("#channels").append(li);
    });
});

function loadChannel (channel) {
    console.log("ON CLICK TRIGGER!!");
    document.getElementById('channelHead').innerHTML = channel;
    localStorage.setItem('channel', channel);
    socket.emit('load channel', channel);
};

function constructMessage(text) {
    const now = new Date();

    return {
        'text': text,
        'user': localStorage.getItem('user'),
        'time': now.toLocaleString('en-US', {timeZone: 'EST'}),
        'channel': localStorage.getItem('channel')
    };
};

function clearInput(element) {
    document.getElementById(element).value = '';
};
