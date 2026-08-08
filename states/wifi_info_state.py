from states.carousel_state import CarouselState
import time


class WifiInfoState(CarouselState):

    def __init__(self):
        super().__init__()
        self.last_update = 0

    def enter(self, app):
        print("WiFi info screen")
        app.display.clear()
        self._update_display(app)

    def update(self, app):
        if self.handle_navigation(app):
            return

        now = time.ticks_ms()

        if time.ticks_diff(now, self.last_update) >= 3000:
            self.last_update = now
            self._update_display(app)

    def _update_display(self, app):
        status = "WiFi: OK" if app.wifi.is_connected() else "WiFi: OFF"
        ip = "IP:" + app.wifi.get_ip()

        if ip is None:
            ip = "No IP"

        app.display.set_cursor(0, 0)
        app.display.write("{:<16}".format(status[:16]))

        app.display.set_cursor(1, 0)
        app.display.write("{:<16}".format(ip[:16]))

    def exit(self, app):
        print("Leaving WiFi info")