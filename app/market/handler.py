from sys import exit
from app.market.data.handler import DataHandler
from app.market.model.handler import ModelHandler
from app.market.orders.handler import OrdersHandler

from infrastructure.external_api.market.record.adapter import RecordAdapter

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
        self.__no_data = 0

    def run(self):
        data = self.get_data()
        if data:
            self.__reset_no_data_count()
            new_orders = self.process(data=data)
            self.__check_exit_criteria()
            if new_orders:
                successful_orders = self.place_orders(orders=new_orders)
                self.__fix_item_probability(orders=successful_orders)
                self.__prevent_reorder(orders=successful_orders)
        else:
            self.__increase_no_data_count()

    def get_data(self):
        return self.external_api.get_market()

    def process(self, data):

        self.data.add(data=data)
        model_data = self.data.get_model_data()
        positive_results = self.models.get_results(model_data)
        new_orders = self.orders.get_new_orders(positive_results)

        return new_orders

    def place_orders(self, orders):
        response = self.external_api.post_order(orders=orders)
        successful_order_ids = self.__get_successful_order_ids(response=response)
        successful_orders = self.__get_successful_orders(
            orders=orders, successful_ids=successful_order_ids
        )

        return successful_orders

    def __check_exit_criteria(self):
        self.__exit_if_closed()
        self.__exit_if_no_data()
        return None

    def __exit_if_closed(self):
        if self.data.confirm_market_closed():
            exit(0)

    def __exit_if_no_data(self):
        if self.__no_data >= 10:
            exit(0)

    def __reset_no_data_count(self):
        self.__no_data = 0
        return 0

    def __increase_no_data_count(self):
        self.__no_data += 1
        return None

    def __get_successful_order_ids(self, response):
        return list(
            map(
                lambda order: order.get("instruction").get("selectionId"),
                filter(lambda order: self.__get_successful_order(order), response),
            )
        )

    def __get_successful_order(self, order):
        return order.get("status") == "SUCCESS"

    def __get_successful_orders(self, orders, successful_ids):
        return list(filter(lambda order: order.get("id") in successful_ids, orders))

    def __fix_item_probability(self, orders):
        map(
            lambda order: self.data.set_probability(
                order.get("id"), order.get("probability")
            ),
            orders,
        )
        return None

    def __prevent_reorder(self, orders):
        self.orders.add_processed_orders(orders=orders)
        return None
