from tests.utils import GIVEN, WHEN, THEN, almost_equal
from tests.mock.mediator import MockMediator

from app.market.orders.handler import OrdersHandler

from unittest.mock import patch


@patch("tests.mock.mediator.MockMediator.notify")
def test_empty_items(mock_notify):
    GIVEN("an orders handler and some items")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=5000)
    items = []

    WHEN("we call get_new_orders")
    handler.get_new_orders(items=items)

    THEN("the mediator's notify method is called with the correct paramaters")
    args, kwargs = mock_notify.call_args
    assert args == ()
    assert kwargs.get("event") == "finished processing"
    new_orders = kwargs.get("data")

    THEN("there are no new orders")
    assert not new_orders
    assert new_orders is None


@patch("tests.mock.mediator.MockMediator.notify")
def test_single_item(mock_notify):
    GIVEN("an orders handler and some items")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=5000)
    items = [
        {
            "id": 16397186,
            "probability": 0.19889500121124917,
            "type": "BUY",
            "ex_price": 6.4,
            "returns_price": 6.13,
        }
    ]

    WHEN("we call get_new_orders")
    handler.get_new_orders(items=items)

    THEN("the mediator's notify method is called with the correct paramaters")
    args, kwargs = mock_notify.call_args
    assert args == ()
    assert kwargs.get("event") == "new orders"
    new_orders = kwargs.get("data")

    THEN("the correct order information is returned")
    assert new_orders == [
        {
            "id": 16397186,
            "probability": 0.19889500121124917,
            "type": "BUY",
            "ex_price": 6.4,
            "returns_price": 6.13,
            "min_size": 5,
            "size": 250.0,
            "risk_percentage": 0.05,
        }
    ]

    WHEN("we add the order to the handler (after processing)")
    handler.prevent_reorder(orders=new_orders)
    THEN("the correct information has been added to the handler")
    assert handler.get_orders() == new_orders

    WHEN("we try to add the order to the handler a second time")
    handler.prevent_reorder(orders=new_orders)
    THEN("the order has not been added again to the handler")
    assert handler.get_orders() == new_orders

    WHEN("we try to get new orders again using the same item")
    handler.get_new_orders(items=items)

    THEN("the mediator's notify method is called with the correct paramaters")
    args, kwargs = mock_notify.call_args
    assert args == ()
    assert kwargs.get("event") == "finished processing"
    new_orders = kwargs.get("data")

    THEN("there are no new orders")
    assert not new_orders
    assert new_orders is None


def test_calc_reduced_risk_percentage():
    GIVEN("a set of risk percentages and an orders handler with an existing order")
    items = [
        {"id": 123, "risk_percentage": 0.01},
        {"id": 456, "risk_percentage": 0.01},
        {"id": 789, "risk_percentage": 0.02},
        {"id": 101, "risk_percentage": 0},
    ]
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=5000)
    existing_orders = [
        {
            "id": 999,
            "probability": 0.26,
            "type": "SELL",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.03,
        }
    ]
    handler.prevent_reorder(existing_orders)

    WHEN("we calculate the reduced risk percentages")
    reduced_risk_percentages = handler._calc_reduced_risk_percentage(
        initial_risk_percentage=items
    )

    THEN("the percentages have been reduced")
    assert reduced_risk_percentages.get(123) == 0.01 * (1 - 0.01) * (1 - 0.02) * (
        1 - 0.03
    )
    assert reduced_risk_percentages.get(456) == 0.01 * (1 - 0.01) * (1 - 0.02) * (
        1 - 0.03
    )
    assert reduced_risk_percentages.get(789) == 0.02 * (1 - 0.01) * (1 - 0.01) * (
        1 - 0.03
    )
    assert reduced_risk_percentages.get(101) == 0
    assert reduced_risk_percentages.get(999) is None


def test_calc_order_size():
    GIVEN("a handler and a list of items with risk_percentages")
    bank = 1000
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=bank)
    items = [
        {"id": 123, "risk_percentage": -5},
        {"id": 101, "risk_percentage": 0.001},
        {"id": 456, "risk_percentage": 0.01},
        {"id": 789, "risk_percentage": 0.1},
        {"id": 202, "risk_percentage": 0.156788},
    ]
    WHEN("we calculate the size of the orders")
    for item in items:
        size = handler._calc_order_size(item=item)
        THEN("the correct sizes are returned")
        assert size == round(max(item.get("risk_percentage"), 0) * bank, 2)


def test_calc_risk_percentage():
    GIVEN("a handler, a probability and price")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=1)
    probability = 0.6
    price = 2

    WHEN("we calculate the uncapped risk percentage")
    risk = handler._calc_risk_percentage(
        probability=probability, price=price, kelly_fraction=1, cap=1
    )
    THEN("the correct risk percentage is returned")
    assert almost_equal(risk, ((probability * price) - (1 - probability)) / price)

    WHEN("we calculate cap the risk percentage at 10%")
    capped_risk = handler._calc_risk_percentage(
        probability=probability, price=price, kelly_fraction=1, cap=0.1
    )
    THEN("the correct risk percentage is returned")
    assert capped_risk == 0.1

    WHEN("we calculate the risk percentage based on a reduced kelly fraction")
    fraction = 0.1
    reduced_risk = handler._calc_risk_percentage(
        probability=probability, price=price, kelly_fraction=fraction, cap=1
    )
    THEN("the reduced risk is less than the original risk")
    assert reduced_risk < risk
    THEN("the correct risk percentage is returned")
    assert almost_equal(
        reduced_risk,
        (
            ((probability * price) ** fraction - (1 - probability) ** fraction)
            / (
                (price * probability) ** fraction
                + (price * (1 - probability)) ** fraction
            )
        ),
    )


def test_calc_no_risk_percentage():
    GIVEN("a handler, a probability and an equal price")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=1)
    probability = 0.5
    price = 2

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0

    GIVEN("a handler, a probability and a smaller price")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=1)
    probability = 0.5
    price = 1.5

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0

    GIVEN("a handler, a negative probability and negative price")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=1)
    probability = -0.5
    price = -2.1

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0


def test_add_valid_processed_orders():
    GIVEN("a handler and a set of valid processed orders")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=100000000000)
    processed_orders = [
        {
            "id": 1234,
            "probability": 0.2,
            "type": "BUY",
            "ex_price": 9.1,
            "returns_price": 8.65,
            "min_size": 5,
            "size": 50000,
            "risk_percentage": 0.05,
        },
        {
            "id": 5678,
            "probability": 0.26,
            "type": "SELL",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
    ]
    WHEN("we add the orders to the handler")
    handler.prevent_reorder(orders=processed_orders)
    existing_orders = handler.get_orders()
    THEN("the correct order data has been added to the handler")
    assert existing_orders == processed_orders


def test_add_invalid_processed_orders():
    GIVEN("a handler and a set of valid processed orders")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=100000000000)
    processed_orders = [
        {
            "probability": 0.5,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "no probability",
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "negative probability",
            "probability": -0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "wrong probability",
            "probability": 1.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "no type",
            "probability": 0.26,
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "wrong type",
            "type": "FIXED",
            "probability": 0.26,
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "no buy price",
            "probability": 0.26,
            "type": "BUY",
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "negative buy price",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": -5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "no min size",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "0 min size",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 0,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {
            "id": "no size",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 0,
            "risk_percentage": 0.01,
        },
        {
            "id": "size below min size",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 2,
            "size": 1,
            "risk_percentage": 0.01,
        },
        {
            "id": "no risk percentage",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 2,
            "size": 1,
        },
        {
            "id": "negative risk percentage",
            "probability": 0.26,
            "type": "BUY",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 2,
            "size": 1,
            "risk_percentage": -0.01,
        },
    ]
    WHEN("we try to add the orders to the handler")
    handler.prevent_reorder(orders=processed_orders)
    existing_orders = handler.get_orders()
    THEN("no order data has been added to the handler")
    assert existing_orders == []


def test_add_mixed_processed_orders():
    GIVEN("a handler and a set of processed orders (2 valid, 1 invalid)")
    mediator = MockMediator()
    handler = OrdersHandler(mediator=mediator, bank=100000000000)
    processed_orders = [
        {
            "id": 1234,
            "probability": 0.2,
            "type": "BUY",
            "ex_price": 9.1,
            "returns_price": 8.65,
            "min_size": 5,
            "size": 50000,
            "risk_percentage": 0.05,
        },
        {
            "id": 5678,
            "probability": 0.26,
            "type": "SELL",
            "ex_price": 5,
            "returns_price": 4.75,
            "min_size": 5,
            "size": 10000,
            "risk_percentage": 0.01,
        },
        {},
    ]
    WHEN("we add the orders to the handler")
    handler.prevent_reorder(orders=processed_orders)
    existing_orders = handler.get_orders()
    THEN("the correct number of orders have been added to the handler")
    assert len(existing_orders) == 2
    THEN("the correct order data has been added to the handler")
    assert existing_orders == processed_orders[0:2]
