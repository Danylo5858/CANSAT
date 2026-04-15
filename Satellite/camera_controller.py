import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
from picamera2 import Picamera2
from log_manager import log_queue

log = False
SleepTime = 5

def init(size):
    global picam2, url
    load_dotenv()
    url = str(os.environ.get("LOCAL_URL")) + "/upload"
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={ "size": size }))
    picam2.start()
    time.sleep(2)
    picam2.set_controls({
        "ExposureTime": 1500,
        "AnalogueGain": 2.0,
        "AfMode": 2
    })

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
            result = requests.post(url, files=files, timeout=1)
            if log:
                log_queue.put(f"Imagen enviada por HTTP: {result.text}")
        except Exception as e:
            if log:
                log_queue.put(f"Excepción en captura de imagen: {str(e)}")
        time.sleep(SleepTime)
