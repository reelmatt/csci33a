import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = {}

@app.route("/")
def index():
    return render_template("index.html", channels=channels.keys(), messages=channels)

# Check if the new_channel name already exists
# If it does, return an error to the user
# Otherwise, add entry to dictionary and display on the screen
@socketio.on("create channel")
def create_channel(new_channel):
    name = new_channel["name"]

    print(channels)
    if name in channels:
        message = f"Sorry, the channel '{name}' has already been created. Try another name."
        print(message)
        emit("channel error", message, broadcast=False)
    else:
        # Create an new dictionary entry, with empty message array
        channels[name] = []
        print(channels)
        emit("list channel", name, broadcast=True)

# User clicks on a channel, retrieve any associated messages to load
# onto the screen
@socketio.on("load channel")
def load_channel(channel):
    print(f"In load_channel, name of {channel}.")
    print(f"\n\n\nAll channels are currently")
    print(channels)
    messages = channels[channel]

    print(f"Found {len(messages)} messages for {channel}.")
    if messages:
        emit("load messages", messages, broadcast=False)
    # emit("load messages", {"channel": channel, "messages": messages}, broadcast=False)

# Extract the pieces of the message and add to the appropriate channel entry
# Return it back to the screen to add to list
@socketio.on("send message")
def send_message(data):
    text = data['text']
    user = data['user']
    time = data['time']
    channel = data['channel']

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
