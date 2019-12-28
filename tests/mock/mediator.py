from app.mediator import Mediator


class MockMediator(Mediator):
    def notify(self, data, event):
        pass
