import time
import threading
from multiprocessing import Process, Queue
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
import wireless_communication_gs as wcom_gs
import Server.app as app

server_queue = Queue()
server = Process(target=app.run, args=(server_queue,))
server.start()

threading.Thread(target=lm.logger, daemon=True).start()

wcom_gs.log = True
wcom_gs.init(2, 868)
threading.Thread(target=wcom_gs.receiver, daemon=True).start()

wdf.log = True
gm.log = True

try:
	while True:
		data = wcom_gs.received_data.get()
		server_queue.put(("BMP390_data", data["BMP390"]))
		threads = [
			threading.Thread(target=gm.update_graph, args=(data["BMP390"],), daemon=True)
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
