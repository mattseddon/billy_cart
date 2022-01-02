from app.interface import Interface
from infrastructure.built_in.adapter.abstract_base import abstract_method


class Mediator(metaclass=Interface):
    @abstract_method
    def notify(self, event, data=None):
        pass
