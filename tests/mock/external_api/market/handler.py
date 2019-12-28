from app.market.interface import ExternalAPIMarketInterface


class MockExternalAPIMarketHandler(ExternalAPIMarketInterface):
    def post_order(self, orders):
        orders = list(map(lambda order: self.__make_successful(order), orders))
        return orders

    def __make_successful(self, order):
        return {"status": "SUCCESS", "instruction": {"selectionId": order.get("id")}}

    def get_market(self):
        pass

    def set_mediator(self):
        pass
