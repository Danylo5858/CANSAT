def run(queue, on_request, log):
	import eventlet
	eventlet.monkey_patch()

	import os
	import sys
	from queue import Empty
	from dotenv import load_dotenv
	from flask import Flask, jsonify, render_template, request
	from flask_socketio import SocketIO

	load_dotenv()
	GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

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

	def process_backup(data):
		socketio.emit("backup_response", on_request("backup_request", data))
		if log:
			print("COPIA DE SEGURIDAD EMITIDA")

	@app.route("/")
	def index():
		return render_template("index.html", google_maps_api_key=GOOGLE_MAPS_API_KEY)

	@app.route('/upload', mehtods=['POST'])
	def upload():
		files = request.files.getlist("images")
		saved_files = []
		for file in files:
			filename = file.filename
			file.save(f"uploads/{filename}")
			saved_files.append(filename)
		return { "status": "ok", "received": saved_files }

	@socketio.on("connect")
	def handle_connect():
		if log:
			print("CLIENTE CONECTADO")

	@socketio.on("backup_request")
	def handle_backup_request(data):
		if log:
			print(f"PETICION DE COPIA DE SEGURIDAD: {data}")
		socketio.start_background_task(process_backup, data)

	if log:
		print("SERVER RUNNING")
	socketio.start_background_task(forward)
	socketio.run(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
	run(None, lambda request, req_data: None, True)
