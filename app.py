import time


class App:

    def __init__(self, wifi_service, time_service, display_service):
        self.wifi = wifi_service
        self.time_service = time_service
        self.display = display_service

        self.state = None
        self.running = True

    def change_state(self, new_state):
        if self.state is not None:
            print(
                "Leaving state:",
                self.state.__class__.__name__
            )

            self.state.exit(self)

        self.state = new_state

        print(
            "Entering state:",
            self.state.__class__.__name__
        )

        self.state.enter(self)

    def run(self):
        while self.running:
            if self.state is not None:
                self.state.update(self)

            time.sleep_ms(50)