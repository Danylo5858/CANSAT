import time
import subprocess
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
            filename = f"Pictures/{time.time()}.jpg"
            picam2.capture_file(filename)
            if log:
                log_queue.put(f"Imagen guardada: {filename}")
        except Exception as e:
            if log:
                log_queue.put(f"Excepción en captura de imagen: {str(e)}")
        time.sleep(SleepTime)

# def capture():
#     while True:
#         try:
#             timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#             filename = f"Pictures/{timestamp}.jpg"
#             cmd = [
#                 "libcamera-still",
#                 "-o", filename,
#                 "--width", "512",
#                 "--height", "512",
#                 "--nopreview"
#             ]
#             result = subprocess.run(
#                 cmd,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )
#             if result.returncode != 0:
#                 error_msg = result.stderr.strip()
#                 if log:
#                     log_queue.put(f"Error capturando imagen: {error_msg}")
#             else:
#                 if log:
#                     log_queue.put(f"Imagen guardada: {filename}")
#         except Exception as e:
#             if log:
#                 log_queue.put(f"Excepción en captura de imagen: {str(e)}")
#         time.sleep(5)
