from states.base_state import BaseState
from states.home_state import HomeState
from states.error_state import ErrorState


class TimeSyncState(BaseState):

    def __init__(self):
        self.sync_attempted = False

    def enter(self, app):
        print("Time sync state started")

    def update(self, app):
        if self.sync_attempted:
            return

        self.sync_attempted = True

        success = app.time_service.sync()

        if success:
            app.change_state(HomeState())
        else:
            app.change_state(
                ErrorState("Could not synchronize internet time")
            )

    def exit(self, app):
        print("Time sync state finished")