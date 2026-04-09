import time
import subprocess
from datetime import datetime
from log_manager import log_queue

log = False

def capture():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Pictures/{timestamp}.jpg"
            cmd = [
                "libcamera-still",
                "-o", filename,
                "--width", "512",
                "--height", "512",
                "--nopreview"
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if log:
                    log_queue.put(f"Error capturando imagen: {error_msg}")
            else:
                if log:
                    log_queue.put(f"Imagen guardada: {filename}")
        except Exception as e:
            if log:
                log_queue.put(f"Excepción en captura de imagen: {str(e)}")
        time.sleep(5)
