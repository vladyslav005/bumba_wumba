class ScreenNavigator:

    def __init__(self, screens):
        self.screens = screens

    def next(self, current_state):
        index = self._get_index(current_state)
        next_index = (index + 1) % len(self.screens)
        return self.screens[next_index]()

    def previous(self, current_state):
        index = self._get_index(current_state)
        previous_index = (index - 1) % len(self.screens)
        return self.screens[previous_index]()

    def _get_index(self, current_state):
        current_class = current_state.__class__

        for i, state_class in enumerate(self.screens):
            if state_class == current_class:
                return i

        return 0