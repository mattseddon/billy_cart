from app.interface import Interface
from infrastructure.built_in.adapter.abstract_base import abstract_method


class ExternalAPIMarketInterface(metaclass=Interface):
    @abstract_method
    def get_market(self):
        pass

    @abstract_method
    def post_order(self):
        pass

    @abstract_method
    def set_mediator(self):
        pass
