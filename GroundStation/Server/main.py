def run(queue, on_request, log):
	import eventlet
	eventlet.monkey_patch()

	import os
	import sys
	from queue import Empty
	from flask import Flask, jsonify, render_template
	from flask_socketio import SocketIO

	app = Flask(__name__)
	socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

	def forward():
		if queue is not None:
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
		if log:
			print("CLIENTE CONECTADO")

	@socketio.on("backup_request")
	def handle_backup_request(data):
		if log:
			print(f"BACKUP REQUEST: {data}")
		socketio.start_background_task(target=on_request, args=("backup_request", data))

	if log:
		print("SERVER RUNNING")
	socketio.start_background_task(forward)
	socketio.run(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
	run(None, lambda data: None, True)
