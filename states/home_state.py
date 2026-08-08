from states.base_state import BaseState
import time


class HomeState(BaseState):

    def __init__(self):
        self.last_update = 0

    def enter(self, app):
        print("System ready")
        self._update_display(app)

    def update(self, app):
        now = time.ticks_ms()

        # Update display every second
        if time.ticks_diff(now, self.last_update) >= 1000:
            self.last_update = now
            self._update_display(app)

    def _update_display(self, app):
        current = app.time_service.get_time()

        year = current[0]
        month = current[1]
        day = current[2]
        hour = current[3]
        minute = current[4]
        second = current[5]

        date_text = "{:02d}.{:02d}.{:04d}".format(
            day,
            month,
            year
        )

        time_text = "{:02d}:{:02d}:{:02d}".format(
            hour,
            minute,
            second
        )

        app.display.set_cursor(0, 0)
        app.display.write("{:<16}".format(date_text))
        app.display.set_cursor(1, 0)
        app.display.write("{:<16}".format(time_text))

    def exit(self, app):
        print("Leaving home")