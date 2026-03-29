import os
import sys
import signal
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
import time

sys.path.append(os.path.abspath(".."))
from log_manager import log_queue

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
	time.sleep(7)
	log_queue.put("SERVERRRRR")
	def handle_sigterm(signum, frame):
		print("Apagando servidor correctamente...")
		exit(0)

	signal.signal(signal.SIGTERM, handle_sigterm)

	socketio.run(app, host="0.0.0.0", port=5000)

def send_data(name, data):
	socketio.emit(name, data)
