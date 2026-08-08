import time


class TelemetryService:

    def __init__(
        self,
        dht_service,
        air_service,
        persistence_service,
        interval_ms=30000
    ):
        self.dht = dht_service
        self.air = air_service
        self.persistence = persistence_service

        self.interval_ms = interval_ms
        self.last_save = time.ticks_ms()

    def update(self):
        now = time.ticks_ms()

        if time.ticks_diff(now, self.last_save) < self.interval_ms:
            return

        self.last_save = now

        climate = self.dht.read()
        air = self.air.read()

        if climate is None:
            print("Telemetry: DHT data unavailable")
            return

        if air is None:
            print("Telemetry: air data unavailable")
            return

        temperature = climate["temperature"]
        humidity = climate["humidity"]
        eco2 = air["eco2"]
        tvoc = air["tvoc"]

        print(
            "Telemetry:",
            temperature, "C",
            humidity, "%",
            eco2, "ppm",
            tvoc, "ppb"
        )

        self.persistence.save(
            temperature=temperature,
            humidity=humidity,
            eco2=eco2,
            tvoc=tvoc
        )