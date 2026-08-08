import network
import time


class WiFiService:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

        self.wlan = network.WLAN(network.WLAN.IF_STA)

    def connect(self, timeout_seconds=10):
        if self.wlan.isconnected():
            print("WiFi already connected")
            return True

        print("Connecting to WiFi...")

        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)

        start = time.time()

        while not self.wlan.isconnected():
            if time.time() - start >= timeout_seconds:
                print("WiFi connection timeout")
                return False

            time.sleep(0.2)

        print("WiFi connected")
        print("IP:", self.get_ip())

        return True

    def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)

        print("WiFi disconnected")

    def is_connected(self):
        return self.wlan.isconnected()

    def get_ip(self):
        if not self.is_connected():
            return None

        return self.wlan.ifconfig()[0]

    def get_status(self):
        return self.wlan.status()