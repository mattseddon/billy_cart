from app.mediator import Mediator


class Colleague:
    def __init__(self, mediator: Mediator):
        self._mediator = mediator

    @property
    def mediator(self):
        return self._mediator

    def set_mediator(self, mediator: Mediator):
        self._mediator = mediator
