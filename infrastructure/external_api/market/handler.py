from infrastructure.external_api.handler import ExternalAPIHandler
from app.market.interface import ExternalAPIMarketInterface
from private.details import get_orders_str, get_market_str


class ExternalAPIMarketHandler(ExternalAPIHandler, ExternalAPIMarketInterface):
    def __init__(self, market_id, headers, environment="Prod"):
        ExternalAPIHandler.__init__(self, environment=environment)
        self.__market_id = market_id
        self._headers = headers

    def get_market(self):

        request = (
            '{"jsonrpc": "2.0", "method": "%s",'
            '"params":{"marketIds":[%s],'
            '"priceProjection":{"priceData":["EX_BEST_OFFERS","SP_AVAILABLE","SP_TRADED","EX_TRADED"]},'
            '"marketProjection":["MARKET_START_TIME"]}, "id": 1}'
        ) % (get_market_str(), self.__market_id)

        market = self._call_exchange(request=request)
        return market[0] if market else {}

    def post_order(self, orders):

        valid_orders = self._validate_orders(orders=orders)

        if valid_orders:
            request = (
                '{"jsonrpc": "2.0","method": "%s",'
                '"params":{"marketId": "%s","instructions":[%s]}'
                ',"id": 1}'
            ) % (
                get_orders_str(),
                self.__market_id,
                self.__get_orders_str(orders=valid_orders),
            )

            result = self._post_instructions(request=request)

        return result

    def _validate_orders(self, orders):
        valid_orders = list(filter(lambda order: self.__is_valid(order=order), orders))
        return valid_orders

    def __is_valid(self, order):
        try:
            is_valid = (
                order.get("id") > 0
                and order.get("type") in ["BUY", "SELL"]
                and order.get("ex_price") > 0
                and order.get("size") > 0
            )
        except:
            is_valid = False
        return is_valid

    def __get_orders_str(self, orders):
        order_list = list(map(lambda order: self.__get_order_str(order=order), orders))
        return ",".join(order_list)

    def __get_order_str(self, order):
        return (
            '{"selectionId":"%s","handicap": "0","side": "%s","orderType": "LIMIT",'
            '"limitOrder":{"size": "%.2f","price": "%.1f","persistenceType": "LAPSE"}}'
        ) % (
            order.get("id"),
            "LAY" if order.get("type") == "SELL" else "BACK",
            order.get("size"),
            order.get("ex_price"),
        )
