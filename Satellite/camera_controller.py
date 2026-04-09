import time
from datetime import datetime
from picamera2 import Picamera2
from log_manager import log_queue

log = False
SleepTime = 5

def init(size):
    global picam2
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={ "size": size }))
    picam2.start()

def capture():
    while True:
        try:
            filename = f"Pictures/{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpg"
            picam2.capture_file(filename)
            if log:
                log_queue.put(f"Imagen guardada: {filename}")
        except Exception as e:
            if log:
                log_queue.put(f"Excepción en captura de imagen: {str(e)}")
        time.sleep(SleepTime)
