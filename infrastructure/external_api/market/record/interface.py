from app.interface import Interface
from infrastructure.class_construction.abstract_base import abstract_method


class ItemAdapterInterface(metaclass=Interface):
    @abstract_method
    def get_adapted_data(self):
        pass
