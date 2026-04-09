import os
import time
import subprocess
from datetime import datetime

os.makedirs("Pictures", exist_ok=True)

try:
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Pictures/{timestamp}.jpg"
        cmd = [
            "libcamera-still",
            "-o", filename,
            "--width", "640",
            "--height", "480",
            "--nopreview"
        ]
        subprocess.run(cmd)
        print(f"Foto guardada: {filename}")
        time.sleep(5)
except KeyboardInterrupt:
    print("\nDetenido")
