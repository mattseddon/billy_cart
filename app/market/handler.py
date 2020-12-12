from app.mediator import Mediator
from app.colleague import Colleague

from app.market.data.handler import DataHandler
from app.market.model.handler import ModelHandler
from app.market.orders.handler import OrdersHandler

from infrastructure.external_api.market.record.adapter import (
    ExternalAPIMarketRecordAdapter,
)

from infrastructure.built_in.adapter.system import die
from infrastructure.third_party.adapter.data_container import DataContainer
from infrastructure.third_party.adapter.stats_model import WeightedLinearRegression


class MarketHandler(Mediator):
    def __init__(
        self,
        market_id,
        external_api,
        market_start_time,
        data_adapter=None,
        data=None,
        models=None,
        orders=None,
    ):

        self.__market_id = market_id

        self.external_api: Colleague = external_api

        adapter = data_adapter or ExternalAPIMarketRecordAdapter(
            market_start_time=market_start_time
        )
        self.data: Colleague = data or DataHandler(
            mediator=self, adapter=adapter, container=DataContainer(),
        )

        self.models: Colleague = models or ModelHandler(
            mediator=self, wls_model=WeightedLinearRegression()
        )

        self.orders: Colleague = orders or OrdersHandler(mediator=self)

        self.__recipients = {
            "external data fetched": self.data.process_data,
            "data added to container": self.models.run_models,
            "models have results": self.orders.get_new_orders,
            "new orders": self.external_api.post_order,
            "orders posted": self.__delegate_posted_orders,
            "market closed": self.__exit,
            "no data provided multiple times": self.__exit,
            "finished processing": self.__finish,
        }

    def run(self):
        self.external_api.get_market()

    def notify(self, event, data=None):
        return self.__recipients.get(event)(data)

    def get_market_id(self):
        return self.__market_id

    def __delegate_posted_orders(self, data):
        successful_orders = self.orders.get_successful_orders(
            response=data.get("response"), orders=data.get("orders")
        )

        self.data.fix_probabilities(items=successful_orders)
        self.orders.prevent_reorder(orders=successful_orders)

    def __finish(self, data):
        pass

    def __exit(self, data):
        die(0)
