from states.carousel_state import CarouselState
import time


class ClimateState(CarouselState):

    def __init__(self):
        super().__init__()
        self.last_update = 0

    def enter(self, app):
        print("Climate screen")
        app.display.clear()
        self._update_display(app)

    def update(self, app):
        if self.handle_navigation(app):
            return

        now = time.ticks_ms()

        if time.ticks_diff(now, self.last_update) >= 2000:
            self.last_update = now
            self._update_display(app)

    def _update_display(self, app):
        data = app.dht.read()

        if data is None:
            line1 = "DHT ERROR"
            line2 = "Try again..."
        else:
            temperature = data["temperature"]
            humidity = data["humidity"]

            line1 = "Temp: {} C".format(temperature)
            line2 = "Humidity:{}%".format(humidity)

        app.display.set_cursor(0, 0)
        app.display.write("{:<16}".format(line1[:16]))

        app.display.set_cursor(1, 0)
        app.display.write("{:<16}".format(line2[:16]))

    def exit(self, app):
        print("Leaving climate")