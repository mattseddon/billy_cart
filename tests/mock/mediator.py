from app.mediator import Mediator


class MockMediator(Mediator):
    def notify(self, event, data=None):
        pass
