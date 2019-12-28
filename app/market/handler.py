from sys import exit
from app.mediator import Mediator
from app.market.data.handler import DataHandler
from app.market.model.handler import ModelHandler
from app.market.orders.handler import OrdersHandler

from infrastructure.external_api.market.record.adapter import RecordAdapter

from infrastructure.third_party.adapter.data_container import DataContainer
from infrastructure.third_party.adapter.stats_model import WeightedLinearRegression

# controls all of the higher level modules
class MarketHandler(Mediator):
    def __init__(
        self, market_id, external_api, data=None, models=None, orders=None,
    ):
        self.external_api = external_api
        self.data = data or DataHandler(
            mediator=self, adapter=RecordAdapter(), container=DataContainer()
        )
        self.models = models or ModelHandler(
            mediator=self, wls_model=WeightedLinearRegression()
        )
        self.orders = orders or OrdersHandler(mediator=self)

    def run(self):
        self.external_api.get_market()

    def notify(self, event, data=None):

        if event == "external data fetched":
            self.data.process_data(data=data)

        elif event == "data added to container":
            self.models.run_models(items=data)

        elif event == "models have results":
            self.orders.get_new_orders(items=data)

        elif event == "new orders":
            self.external_api.post_order(orders=data)

        elif event == "orders posted":
            successful_orders = self.orders.get_successful_orders(
                response=data.get("response"), orders=data.get("orders")
            )

            self.data.fix_probabilities(items=successful_orders)
            self.orders.prevent_reorder(orders=successful_orders)

        elif event == "finished processing":
            # stop
            pass

        elif event in ["market closed", "no data provided multiple times"]:
            exit(0)
