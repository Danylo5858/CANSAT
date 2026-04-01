import time
import threading
from multiprocessing import Process, Queue
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
import wireless_communication_gs as wcom_gs
import Server.main as app

wcom_gs.log = False
wdf.log = True
gm.log = True

server_queue = Queue()
server = Process(target=app.run, args=(server_queue,))
server.start()

threading.Thread(target=lm.logger, daemon=True).start()

wcom_gs.init(2, 868)
threading.Thread(target=wcom_gs.receiver, daemon=True).start()

wdf.init()

try:
	while True:
		cansat_data = wcom_gs.received_data.get()
		server_queue.put(("BMP390_data", cansat_data["BMP390"]))
		wdf.lat = cansat_data["GPS"]["latitude"]
		wdf.lon = cansat_data["GPS"]["longitude"]
		ground_data = wdf.fetch()
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
