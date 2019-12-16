from app.market.data.handler import DataHandler
from app.market.model.handler import ModelHandler
from app.market.orders.handler import OrdersHandler

from infrastructure.external_api.market.handler import ExternalAPIMarketHandler
from infrastructure.external_api.market.adapter.record import RecordAdapter

from infrastructure.third_party.adapter.data_container import DataContainer
from infrastructure.third_party.adapter.stats_model import WeightedLinearRegression

# controls all of the higher level modules
class MarketHandler:
    def __init__(
        self,
        market_id,
        external_api,
        data=DataHandler(adapter=RecordAdapter(), container=DataContainer()),
        models=ModelHandler(wls_model=WeightedLinearRegression()),
        orders=OrdersHandler(),
    ):
        self.external_api = external_api
        self.data = data
        self.models = models
        self.orders = orders

    def stub(self):  # need to work out how to schedule this to run every 5 seconds
        data = self.get_data()
        # if in_play: exit() sub_task
        if data:
            self.process(data)

    def get_data(self):
        return self.external_api.get_market()

    def process(self, data):

        self.data.add(data)
        model_data = self.data.get_model_data()
        positive_results = self.models.get_results(model_data)
        orders = self.orders.get_new_orders(positive_results)
        if orders:
            for order in orders:
                self.data.set_probability(order.get("id"), order.get("probability"))
            self.place_orders(orders=orders)

        return None

    def place_orders(self, orders):
        self.external_api.post_order(orders=orders)
        return None
