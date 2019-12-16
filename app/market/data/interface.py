from app.interface import Interface
from infrastructure.class_construction.abstract_base import abstract_method


class ExternalAPIMarketDataInterface(metaclass=Interface):
    @abstract_method
    def convert(self):
        pass


class DataContainerInterface(metaclass=Interface):
    @abstract_method
    def all_the_methods(self):
        pass
