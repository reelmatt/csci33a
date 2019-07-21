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
    messages = channels[channel]

    if messages:
        emit("load messages", messages, broadcast=False)

# Extract the pieces of the message and add to the appropriate channel entry
# Return it back to the screen to add to list
@socketio.on("send message")
def send_message(message):
    channel = message['channel']
    messages = channels[channel]

    # Limit of 100 messages per channel, remove from start of list
    if len(messages) >= 100:
        messages.pop(0)

    # Add new message and notify clients
    messages.append(message)
    emit("receive message", message, broadcast=True)

# Delete message from Python memory and notify browsers
@socketio.on("delete message")
def delete_message(message):
    # Retrieve the list of messages for the channel
    channel = message['channel']
    messages = channels[channel]

    # Search through the messages to find the one to delete
    for storedMessage in messages:
        # Got a match, delete from list and notify browsers
        if storedMessage == message:
            messages.remove(storedMessage)
            emit("remove message", message, broadcast=True)
            return
