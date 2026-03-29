from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
import eventlet
from log_manager import log_queue

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

def SendData(data):
	socketio.emit("BMP390_data", data)

@app.route("/")
def index():
	return render_template("index.html")

@socketio.on("connect")
def handle_connect():
	log_queue.put("Cliente conectado")

if __name__ == "__main__":
	socketio.run(app, host="0.0.0.0", port=5000)
