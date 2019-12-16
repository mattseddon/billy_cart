from tests.utils import GIVEN, WHEN, THEN, should_test_real_api, lists_are_equal
from infrastructure.external_api.schedule.handler import ExternalAPIScheduleHandler
from infrastructure.external_api.market.handler import ExternalAPIMarketHandler
from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.built_in.adapter.json_utils import make_dict
from unittest.mock import patch

if should_test_real_api():

    def test_get_data():

        GIVEN(
            "a schedule handler and a market handler connected to the dev environment"
        )
        schedule_handler = ExternalAPIScheduleHandler(environment="Dev")
        headers = schedule_handler.get_headers()
        markets = schedule_handler.get_schedule("7", DateTime.utc_5_minutes_from_now())

        WHEN(
            "we create an instance of the market handler for each market and ask for data"
        )
        for market in markets:
            market_id = market.get("marketId")

            market_handler = ExternalAPIMarketHandler(
                environment="Dev", headers=headers, market_id=market_id
            )
            market_info = market_handler.get_market()

            THEN("a dict is returned")
            assert type(market_info) is dict
            if market_info:
                THEN("the dict contains a list of items")
                items = market_info.get("runners")
                assert type(items) is list


@patch(
    "infrastructure.external_api.market.handler.ExternalAPIMarketHandler._call_exchange"
)
def test_post_data(_call_exchange):

    GIVEN("a market handler and some orders")
    market_handler = ExternalAPIMarketHandler(
        environment="Dev", headers={}, market_id=123456
    )
    orders = [
        {"id": 9999999, "type": "BUY", "size": 100, "price": 2.0},
        {"id": 8888888, "type": "SELL", "size": 6.18, "price": 75.0},
        {"id": 7777777, "type": "BUY", "size": 5, "price": 12.6},
    ]
    WHEN("we post the orders")
    market_handler.post_order(orders=orders)
    THEN("the orders can be converted from json to a dict")
    args, kwargs = _call_exchange.call_args
    request = make_dict(kwargs.get("request"))
    expected_request = get_expected()
    assert args == ()
    assert request.get("params").get("instructions") == expected_request.get(
        "params"
    ).get("instructions")


def test_valid_orders():
    GIVEN("a market handler and a set of valid orders")
    market_handler = ExternalAPIMarketHandler(
        environment="Dev", headers={}, market_id=123456
    )
    orders = [
        {"id": 9999999, "type": "BUY", "size": 100, "price": 2.0},
        {"id": 8888888, "type": "SELL", "size": 6.18, "price": 75.0},
        {"id": 7777777, "type": "BUY", "size": 5, "price": 12.6},
    ]
    WHEN("we validate the orders")
    valid_orders = market_handler._validate_orders(orders=orders)
    THEN("all of the orders are shown to be valid")
    assert valid_orders == orders


def test_invalid_order():
    GIVEN("a market handler and an invalid order")
    market_handler = ExternalAPIMarketHandler(
        environment="Dev", headers={}, market_id=123456
    )
    orders = [
        {"type": "BUY", "size": 100, "price": 2.0},
    ]
    valid_orders = market_handler._validate_orders(orders=orders)
    THEN("the order is marked as invalid and omitted from the returned list")
    assert valid_orders == []


def test_valid_and_invalid_orders():
    GIVEN("a market handler two valid orders and two invalid orders")
    market_handler = ExternalAPIMarketHandler(
        environment="Dev", headers={}, market_id=123456
    )
    orders = [
        {"id": 9999999, "size": 100, "price": 2.0},
        {"id": 8888888, "type": "SELL", "size": 6.18, "price": 75.0},
        {"id": 7777777, "type": "BUY", "size": 5, "price": 12.6},
        {"id": 7777777, "type": "BUY", "size": 5, "price": "THE BEST YOU HAVE"},
    ]
    valid_orders = market_handler._validate_orders(orders=orders)
    THEN("the valid orders are returned")
    assert valid_orders == orders[1:3]


def get_expected():
    return {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/placeOrders",
        "params": {
            "marketId": "123456",
            "instructions": [
                {
                    "selectionId": "9999999",
                    "handicap": "0",
                    "side": "BACK",
                    "orderType": "LIMIT",
                    "limitOrder": {
                        "size": "100.00",
                        "price": "2.0",
                        "persistenceType": "LAPSE",
                    },
                },
                {
                    "selectionId": "8888888",
                    "handicap": "0",
                    "side": "LAY",
                    "orderType": "LIMIT",
                    "limitOrder": {
                        "size": "6.18",
                        "price": "75.0",
                        "persistenceType": "LAPSE",
                    },
                },
                {
                    "selectionId": "7777777",
                    "handicap": "0",
                    "side": "BACK",
                    "orderType": "LIMIT",
                    "limitOrder": {
                        "size": "5.00",
                        "price": "12.6",
                        "persistenceType": "LAPSE",
                    },
                },
            ],
        },
        "id": 1,
    }
