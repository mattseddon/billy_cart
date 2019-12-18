from app.interface import Interface
from infrastructure.built_in.adapter.abstract_base import abstract_method


class ItemAdapterInterface(metaclass=Interface):
    @abstract_method
    def get_adapted_data(self):
        pass
