import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = {}

@app.route("/")
def index():
    # messages = channels["channel"]["messages"]
    # print(f"Found messages for {channel}. They are...")
    # print({messages})
    return render_template("index.html", channels=channels.keys())


@app.route("/create", methods=["POST"])
def create():
    channel = request.form.get("channel")
    print(f"Submitted form. New channel name is {channel}.")
    # channels.append(channel)
    if channel in channels:
        message = "Sorry, that channel has already been created. Try another."
        print(message)
        emit("channel error", message, broadcast=False)
        return jsonify({"success": False, "channel": channel})
    else:
        channels[channel] = []
        # channel = {
        #     "name": name,
        #     "messages": []
        # }
        # print(channel)
        # channels.append(channel)
        print(channels)
        emit("channel list", channel, broadcast=True)
        return jsonify({"success": True, "channel": channel})




@socketio.on("create channel")
def create_channel(new_channel):
    name = new_channel["name"]
    print(f"In python, create_channel, data is {name}")


    print(channels)
    if name in channels:
        message = "Sorry, that channel has already been created. Try another."
        print(message)
        emit("channel error", message, broadcast=False)
    else:
        channels[name] = []
        print(channels)
        emit("channel list", {'channel': name, 'messages': channels[name]}, broadcast=True)



@socketio.on("load channel")
def load_channel(channel):

    print(f"In load_channel, name of {channel}.")
    print(f"\n\n\nAll channels are currently")
    print(channels)
    messages = channels[channel]
    # messages = channels.get(channel)
    print(f"Found {len(messages)} messages for {channel}.")
    emit("load messages", {"channel": channel, "messages": messages}, broadcast=False)



@socketio.on("send message")
def send_message(data):
    text = data['text']
    user = data['user']
    time = data['time']
    channel = data['channel']

    print(f"HERE IN SEND MESSAGE")
    print(data)

    # channels[channel].extend(text)
    message = {
        "text": text,
        "user": user,
        "channel": channel
    }
    print(f"ADDED TO CHANNEL...\n\n\n\n")
    channels[channel].append(data)
    messages = channels[channel]
    print(channels)
    print(channels[channel])
    print(f"There are currently {len(messages)} messages.")

    emit("receive message", data, broadcast=True)
