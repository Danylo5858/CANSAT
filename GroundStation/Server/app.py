import os
import sys
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

def init():
	global app, socketio
	app = Flask(__name__)
	socketio = SocketIO(app, cors_allowed_origins="*")

	@app.route("/")
	def index():
		return render_template("index.html")

	@socketio.on("connect")
	def handle_connect():
		log_queue.put("Cliente conectado")

def run():
	print("SERVER RUNNING")
	socketio.run(app, host="0.0.0.0", port=5000)

def send_data(name, data):
	print("Emitiendo datos:", name)
	print(data)
	socketio.emit(name, data)
