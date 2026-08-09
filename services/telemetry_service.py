import time


class TelemetryService:

    def __init__(
        self,
        dht_service,
        air_service,
        persistence_service,
        wifi_service=None,
        rgb_service=None,
        interval_ms=30000,
        sample_interval_ms=1000
    ):
        self.dht = dht_service
        self.air = air_service
        self.persistence = persistence_service
        self.wifi = wifi_service
        self.rgb = rgb_service

        self.interval_ms = interval_ms
        self.sample_interval_ms = sample_interval_ms
        self.window_start_ms = time.ticks_ms()
        self.last_sample_ms = time.ticks_ms() - sample_interval_ms
        self.sample_count = 0
        self.temperature_sum = 0.0
        self.humidity_sum = 0.0
        self.eco2_sum = 0.0
        self.tvoc_sum = 0.0

    def update_led_from_air_quality(self, eco2, tvoc):
        if self.rgb is None:
            return

        if eco2 >= 1200 or tvoc >= 300:
            self.rgb.red()
        elif eco2 >= 800 or tvoc >= 150:
            self.rgb.yellow()
        else:
            self.rgb.green()

    def _reset_window(self, now=None):
        if now is None:
            now = time.ticks_ms()

        self.window_start_ms = now
        self.sample_count = 0
        self.temperature_sum = 0.0
        self.humidity_sum = 0.0
        self.eco2_sum = 0.0
        self.tvoc_sum = 0.0

    def _persist_window(self, now=None):
        if now is None:
            now = time.ticks_ms()

        if self.sample_count == 0:
            print("Telemetry: no samples collected for persistence window")
            return

        temperature = self.temperature_sum / self.sample_count
        humidity = self.humidity_sum / self.sample_count
        eco2 = int(round(self.eco2_sum / self.sample_count))
        tvoc = int(round(self.tvoc_sum / self.sample_count))

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

    def update(self):
        now = time.ticks_ms()

        if time.ticks_diff(now, self.last_sample_ms) < self.sample_interval_ms:
            return

        self.last_sample_ms = now

        climate = self.dht.read()
        air = self.air.read()

        if climate is not None and air is not None:
            self.sample_count += 1
            self.temperature_sum += climate["temperature"]
            self.humidity_sum += climate["humidity"]
            self.eco2_sum += air["eco2"]
            self.tvoc_sum += air["tvoc"]
            self.update_led_from_air_quality(air["eco2"], air["tvoc"])
        else:
            # Skip samples that are not ready yet. The display can still show
            # the last good value, and we do not want to spam the logs.
            return

        if time.ticks_diff(now, self.window_start_ms) < self.interval_ms:
            return

        self._persist_window(now)
        self._reset_window(now)