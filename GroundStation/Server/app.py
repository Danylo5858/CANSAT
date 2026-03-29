def run(queue):
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
			eventlet.sleep(0)
			name, data = queue.get()
			print("Emitiendo datos:", name)
			socketio.emit(name, data)

	@app.route("/")
	def index():
		return render_template("index.html")

	@socketio.on("connect")
	def handle_connect():
		print("CLIENTE CONECTADO")

	print("SERVER RUNNING")
	socketio.start_background_task(forward)
	socketio.run(app, host="0.0.0.0", port=5000)
