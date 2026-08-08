from states.base_state import BaseState


class ErrorState(BaseState):

    def __init__(self, message):
        self.message = message

    def enter(self, app):
        print("ERROR:", self.message)

    def update(self, app):
        pass

    def exit(self, app):
        pass