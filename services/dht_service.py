import dht
from machine import Pin


class DHTService:

    def __init__(self, pin=15):
        self.sensor = dht.DHT11(Pin(pin))

    def read(self):
        try:
            self.sensor.measure()

            return {
                "temperature": self.sensor.temperature(),
                "humidity": self.sensor.humidity()
            }

        except Exception as error:
            print("DHT error:", error)
            return None