from sx126x import sx126x
import time

print("\n===================================")
print("  WAVESHARE SX126X SELF TEST")
print("===================================\n")

# -----------------------------
# 1. CREAR OBJETO (CONFIG INICIAL)
# -----------------------------
print("[1] Initializing module...")

radio = sx126x(
    serial_num="/dev/serial0",
    freq=868,
    addr=0x0001,
    power=22,
    rssi=True
)

print("✔ Object created\n")

# -----------------------------
# 2. PROBAR GET SETTINGS
# -----------------------------
print("[2] Reading settings from module...")

try:
    radio.get_settings()
    print("✔ Settings command sent\n")
except Exception as e:
    print("✖ Error calling get_settings:", e)

# -----------------------------
# 3. RECONFIGURAR (RE-SET)
# -----------------------------
print("[3] Reconfiguring module (no RF test)...")

try:
    radio.set(
        freq=868,
        addr=0x0001,
        power=22,
        rssi=True,
        air_speed=2400,
        net_id=0,
        buffer_size=240,
        crypt=0
    )
    print("✔ Configuration applied\n")
except Exception as e:
    print("✖ Config failed:", e)

# -----------------------------
# 4. VERIFICAR ESTADO GPIO
# -----------------------------
print("[4] Checking GPIO mode states...")

import RPi.GPIO as GPIO

print("M0 state:", GPIO.input(radio.M0))
print("M1 state:", GPIO.input(radio.M1))

# -----------------------------
# 5. VERIFICAR SERIAL BUFFER
# -----------------------------
print("[5] Checking UART buffer...")

time.sleep(0.5)
if radio.ser.inWaiting() > 0:
    data = radio.ser.read(radio.ser.inWaiting())
    print("✔ UART response detected:", data)
else:
    print("No UART data (this can be normal if idle)")

# -----------------------------
# FINAL
# -----------------------------
print("\n===================================")
print("SELF TEST COMPLETE")
print("If no errors appeared, module is OK")
print("===================================\n")
