from queue import Empty

def run(queue, log):
	import eventlet
	eventlet.monkey_patch()

	import os
	import sys
	from flask import Flask, jsonify, render_template
	from flask_socketio import SocketIO

	app = Flask(__name__)
	socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

	def forward():
		while True:
			try:
				name, data = queue.get_nowait()
				if log:
					print("Emitiendo datos:", name)
				socketio.emit(name, data)
			except Empty:
				pass
			socketio.sleep(0.05)

	@app.route("/")
	def index():
		return render_template("index.html")

	@socketio.on("connect")
	def handle_connect():
		print("CLIENTE CONECTADO")

	print("SERVER RUNNING")
	socketio.start_background_task(forward)
	socketio.run(app, host="0.0.0.0", port=5000)
