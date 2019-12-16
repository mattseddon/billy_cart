from app.interface import Interface
from infrastructure.class_construction.abstract_base import abstract_method


class ExternalAPIMarketInterface(metaclass=Interface):
    @abstract_method
    def get_market(self):
        pass

    @abstract_method
    def post_order(self):
        pass
