import time


class TelemetryService:

    def __init__(
        self,
        dht_service,
        air_service,
        persistence_service,
        wifi_service=None,
        rgb_service=None,
        interval_ms=30000
    ):
        self.dht = dht_service
        self.air = air_service
        self.persistence = persistence_service
        self.wifi = wifi_service
        self.rgb = rgb_service

        self.interval_ms = interval_ms
        self.last_save = time.ticks_ms()

    def update_led_from_air_quality(self, eco2, tvoc):
        if self.rgb is None:
            return

        if eco2 >= 1200 or tvoc >= 300:
            self.rgb.red()
        elif eco2 >= 800 or tvoc >= 150:
            self.rgb.yellow()
        else:
            self.rgb.green()

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

        self.update_led_from_air_quality(eco2, tvoc)

        print(
            "Telemetry:",
            temperature, "C",
            humidity, "%",
            eco2, "ppm",
            tvoc, "ppb"
        )
        # If WiFi is available and disconnected, try to reconnect before saving.
        if self.wifi is not None and not self.wifi.is_connected():
            print("Telemetry: WiFi disconnected, attempting reconnect")
            if not self.wifi.connect_with_retries(retries=3, timeout_seconds=10):
                print("Telemetry: unable to reconnect, skipping persistence")
                return

        # Try to persist with a small retry loop in case of transient network errors.
        success = self.persistence.save(
            temperature=temperature,
            humidity=humidity,
            eco2=eco2,
            tvoc=tvoc
        )

        if not success:
            for attempt in range(1, 3):
                print("Telemetry: persistence save failed, retry {}".format(attempt))
                time.sleep(1)
                success = self.persistence.save(
                    temperature=temperature,
                    humidity=humidity,
                    eco2=eco2,
                    tvoc=tvoc
                )

                if success:
                    break