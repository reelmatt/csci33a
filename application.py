import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")


channels = []


@app.route("/create", methods=["POST"])
def create():


    channel = request.form.get("channel")
    print(f"Submitted form. New channel name is {channel}.")
    # channels.append(channel)

    return jsonify({"success": True, "channel": channel})

@socketio.on("create channel")
def create_channel(new_channel):
    print(f"In python, create_channel, data is {new_channel}")
    channels.append(new_channel)
    print(channels)
    emit("channel list", new_channel, broadcast=True)

@socketio.on("load channel")
def load_channel(channel):
    print(f"In load_channel, name of {channel}.");
    
