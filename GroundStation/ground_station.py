import os
import time
import threading
from multiprocessing import Process, Queue
import AI.image_analysis as ai
import backup_manager as bm
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
from log_manager import log_queue
import wireless_communication_gs as wcom_gs
import Server.main as app

wcom_gs.log = True
wdf.log = False
gm.log = False
ai.log = False
server_log = False

os.makedirs("BackupData", exist_ok=True)

def on_request(request, req_data):
	if request == "backup_request":
		return bm.get_backup_data(req_data)
	elif request == "analysis_request":
		return ai.analyse(req_data)

server_queue = Queue()
server = Process(target=app.run, args=(server_queue, on_request, server_log))
server.start()

logger_thread = threading.Thread(target=lm.logger, daemon=True)
logger_thread.start()

wcom_gs.init(2, 869)
receiver_thread = threading.Thread(target=wcom_gs.receiver, daemon=True)
receiver_thread.start()

wdf.init()

try:
	while True:
		cansat_data = wcom_gs.received_data.get()
		server_queue.put(("MPU6050_data", cansat_data["MPU6050"]))
		server_queue.put(("BMP390_data", cansat_data["BMP390"]))
		server_queue.put(("GPS_data", cansat_data["GPS"]))
		if cansat_data["GPS"]["latitude"] != 0 or cansat_data["GPS"]["longitude"] != 0:
			wdf.lat = cansat_data["GPS"]["latitude"]
			wdf.lon = cansat_data["GPS"]["longitude"]
			log_queue.put("GPS actualizo las coordenadas")
		ground_data = wdf.fetch()
		server_queue.put(("ground_data", ground_data))
		threads = [
			threading.Thread(target=gm.update_graph, args=(cansat_data["BMP390"], ground_data), daemon=True)
		]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
except KeyboardInterrupt:
	print("\nCerrando todos los procesos...")
finally:
	if server is not None and server.is_alive():
		print("Apagando servidor...")
		server.terminate()
		server.join()
