import RPi.GPIO as GPIO
import serial
import time

class sx126x:
    """
    Clase para controlar módulos LoRa SX126x desde Raspberry Pi.

    Funcionalidades principales:
    - Configuración del módulo
    - Envío de datos
    - Recepción de datos
    """

    M0 = 22
    M1 = 27

    START_FREQ_850 = 850
    START_FREQ_410 = 410

    UART_BAUDRATE = 9600

    AIR_SPEEDS = {
        1200: 0x01,
        2400: 0x02,
        4800: 0x03,
        9600: 0x04,
        19200: 0x05,
        38400: 0x06,
        62500: 0x07
    }

    POWER_LEVELS = {
        22: 0x00,
        17: 0x01,
        13: 0x02,
        10: 0x03
    }

    BUFFER_SIZES = {
        240: 0x00,
        128: 0x40,
        64: 0x80,
        32: 0xC0
    }

    def __init__(self, serial_port="/dev/ttyS0", freq=868, addr=1, power=22, rssi=False,
                 air_speed=2400, net_id=0, buffer_size=240, crypt=0):
        """
        Inicializa el módulo LoRa.

        Parámetros:
        - serial_port: Puerto UART (ej: /dev/ttyS0)
        - freq: Frecuencia (ej: 868)
        - addr: Dirección del nodo
        - power: Potencia (10, 13, 17, 22)
        - rssi: Activar RSSI (True/False)
        - air_speed: Velocidad LoRa
        - net_id: ID de red
        - buffer_size: Tamaño del paquete
        - crypt: Clave de cifrado
        """

        self.addr = addr
        self.freq = freq
        self.rssi = rssi

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)

        # Serial setup
        try:
            self.ser = serial.Serial(serial_port, self.UART_BAUDRATE, timeout=1)
        except Exception as e:
            raise Exception(f"Error abriendo puerto serial: {e}")

        self._set_mode(config=True)
        self._configure(freq, addr, power, rssi, air_speed, net_id, buffer_size, crypt)
        self._set_mode(config=False)

    def _set_mode(self, config=False):
        """Cambia el modo del módulo."""
        if config:
            GPIO.output(self.M0, GPIO.LOW)
            GPIO.output(self.M1, GPIO.HIGH)
        else:
            GPIO.output(self.M0, GPIO.LOW)
            GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)

    def _configure(self, freq, addr, power, rssi, air_speed, net_id, buffer_size, crypt):
        """Configura el módulo LoRa."""

        if air_speed not in self.AIR_SPEEDS:
            raise ValueError("Velocidad inválida")
        if power not in self.POWER_LEVELS:
            raise ValueError("Potencia inválida")
        if buffer_size not in self.BUFFER_SIZES:
            raise ValueError("Buffer inválido")

        high_addr = (addr >> 8) & 0xFF
        low_addr = addr & 0xFF

        if freq >= 850:
            freq_temp = freq - self.START_FREQ_850
        else:
            freq_temp = freq - self.START_FREQ_410

        cfg = [
            0xC2,
            0x00,
            0x09,
            high_addr,
            low_addr,
            net_id,
            0x60 + self.AIR_SPEEDS[air_speed],
            self.BUFFER_SIZES[buffer_size] + self.POWER_LEVELS[power] + 0x20,
            freq_temp,
            0x43 + (0x80 if rssi else 0x00),
            (crypt >> 8) & 0xFF,
            crypt & 0xFF
        ]

        self.ser.reset_input_buffer()
        self.ser.write(bytes(cfg))
        time.sleep(0.2)

    def send(self, message):
        """
        Envía datos por LoRa.

        Parámetros:
        - message (str o bytes): mensaje a enviar

        Ejemplo:
        >>> lora.send("1,868,Hola")
        """
        self._set_mode(config=False)

        if isinstance(message, str):
            message = message.encode('utf-8')

        self.ser.write(message)
        time.sleep(0.1)

    def receive(self):
        """
        Recibe datos del módulo LoRa.

        Retorna:
        - Lista con los datos separados por comas
        - None si no hay datos

        Ejemplo retorno:
        ["1", "868", "Hola"]
        """
        if self.ser.in_waiting > 0:
            time.sleep(0.2)
            data = self.ser.read(self.ser.in_waiting)

            try:
                message = data[3:].decode('utf-8')
                return message.split(',')
            except Exception:
                return None
        return None
