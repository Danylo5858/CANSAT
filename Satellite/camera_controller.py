import time
import subprocess
from datetime import datetime
from log_manager import log_queue

log = False

def capture():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Pictures/{timestamp}.jpg"
        cmd = [
            "libcamera-still",
            "-o", filename,
            "--width", "512",
            "--height", "512",
            "--nopreview"
        ]
        subprocess.run(cmd)
        if log:
            log_queue.put(f"Foto guardada: {filename}")
        time.sleep(5)
