import time
from datetime import datetime
import requests
from picamera2 import Picamera2
from log_manager import log_queue

log = False
SleepTime = 5
url = "http://10.93.88.51:5000/upload"

def init(size):
    global picam2
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={ "size": size }))
    picam2.start()

def capture():
    while True:
        try:
            filename = f"Pictures/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            picam2.capture_file(filename)
            if log:
                log_queue.put(f"Imagen guardada: {filename}")
            files = {
                "images": open(filename, "rb")
            }
            result = requests.post(url, files=files, timeout=2.5)
            if log:
                log_queue.put(f"Imagen enviada por HTTP: {result.text}")
        except Exception as e:
            if log:
                log_queue.put(f"Excepción en captura de imagen: {str(e)}")
        time.sleep(SleepTime)
