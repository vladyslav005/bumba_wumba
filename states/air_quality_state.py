from states.carousel_state import CarouselState
import time


class AirQualityState(CarouselState):

    def __init__(self):
        super().__init__()
        self.last_update = 0

    def enter(self, app):
        print("Air quality screen")

        app.display.clear()

        app.display.set_cursor(0, 0)
        app.display.write("Air Quality")

        app.display.set_cursor(1, 0)
        app.display.write("Reading...")

    def update(self, app):

        if self.handle_navigation(app):
            return

        now = time.ticks_ms()

        if time.ticks_diff(
            now,
            self.last_update
        ) >= 1000:

            self.last_update = now
            self._update_display(app)

    def _update_display(self, app):

        data = app.air.read()

        if data is None:
            return

        eco2 = data["eco2"]
        tvoc = data["tvoc"]

        print(
            "eCO2:", eco2,
            "TVOC:", tvoc
        )

        # Determine air quality
        if eco2 >= 1200 or tvoc >= 300:

            status = "BAD"
            message = "Air: BAD! VENT"

            app.rgb.red()

        elif eco2 >= 800 or tvoc >= 150:

            status = "OK"
            message = "Air: OK"

            app.rgb.yellow()

        else:

            status = "GOOD"
            message = "Air: GOOD"

            app.rgb.green()

        # Example:
        # eCO2:650 VOC:25
        values = "eCO2:{} VOC:{}".format(
            eco2,
            tvoc
        )

        app.display.set_cursor(0, 0)
        app.display.write(
            "{:<16}".format(message[:16])
        )

        app.display.set_cursor(1, 0)
        app.display.write(
            "{:<16}".format(values[:16])
        )

    def exit(self, app):
        print("Leaving air quality")