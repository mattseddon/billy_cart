from tests.utils import GIVEN, WHEN, THEN, almost_equal
from app.market.orders.handler import OrdersHandler


def test_empty_items():
    GIVEN("an orders handler and some items")
    handler = OrdersHandler(bank=5000)
    items = []

    WHEN("we call get_new_orders")
    new_orders = handler.get_new_orders(items=items)

    THEN("an empty list is returned")
    assert new_orders == []


def test_single_item():
    GIVEN("an orders handler and some items")
    handler = OrdersHandler(bank=5000)
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
    new_orders = handler.get_new_orders(items=items)

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
    handler.add_processed_orders(orders=new_orders)
    THEN("the correct information has been added to the handler")
    assert handler._get_existing_orders() == new_orders

    WHEN("we try to add the order to the handler a second time")
    handler.add_processed_orders(orders=new_orders)
    THEN("the order has not been added again to the handler")
    assert handler._get_existing_orders() == new_orders

    WHEN("we try to get new orders again using the same item")
    new_orders = handler.get_new_orders(items=items)
    THEN("no new orders are returned")
    assert new_orders == []


def test_calc_reduced_risk_percentage():
    GIVEN("a set of risk percentages and an orders handler")
    items = [
        {"id": 123, "risk_percentage": 0.01},
        {"id": 456, "risk_percentage": 0.01},
        {"id": 789, "risk_percentage": 0.02},
        {"id": 101, "risk_percentage": 0},
    ]
    handler = OrdersHandler(bank=5000)

    WHEN("we calculate the reduced risk percentages")
    reduced_risk_percentages = handler._calc_reduced_risk_percentage(
        initial_risk_percentage=items
    )

    THEN("the percentages have been reduced")
    assert reduced_risk_percentages.get(123) == 0.01 * (1 - 0.01) * (1 - 0.02)
    assert reduced_risk_percentages.get(456) == 0.01 * (1 - 0.01) * (1 - 0.02)
    assert reduced_risk_percentages.get(789) == 0.02 * (1 - 0.01) * (1 - 0.01)
    assert reduced_risk_percentages.get(101) == 0


def test_calc_order_size():
    GIVEN("a handler and a list of items with risk_percentages")
    bank = 1000
    handler = OrdersHandler(bank=bank)
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
    handler = OrdersHandler(bank=1)
    probability = 0.6
    price = 2

    WHEN("we calculate the uncapped risk percentage")
    risk = handler._calc_risk_percentage(
        probability=probability, price=price, kf=1, cap=1
    )
    THEN("the correct risk percentage is returned")
    assert almost_equal(risk, ((probability * price) - (1 - probability)) / price)

    WHEN("we calculate cap the risk percentage at 10%")
    capped_risk = handler._calc_risk_percentage(
        probability=probability, price=price, kf=1, cap=0.1
    )
    THEN("the correct risk percentage is returned")
    assert capped_risk == 0.1

    WHEN("we calculate the risk percentage based on a reduced kelly fraction")
    fraction = 0.1
    reduced_risk = handler._calc_risk_percentage(
        probability=probability, price=price, kf=fraction, cap=1
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
    handler = OrdersHandler(bank=1)
    probability = 0.5
    price = 2

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0

    GIVEN("a handler, a probability and a smaller price")
    handler = OrdersHandler(bank=1)
    probability = 0.5
    price = 1.5

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0

    GIVEN("a handler, a negative probability and negative price")
    handler = OrdersHandler(bank=1)
    probability = -0.5
    price = -2.1

    WHEN("we calculate cap the risk percentage at 10%")
    no_risk = handler._calc_risk_percentage(probability=probability, price=price)
    THEN("the correct risk percentage is returned")
    assert no_risk == 0


def test_add_valid_processed_orders():
    GIVEN("a handler and a set of valid processed orders")
    handler = OrdersHandler(bank=100000000000)
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
    handler.add_processed_orders(orders=processed_orders)
    existing_orders = handler._get_existing_orders()
    THEN("the correct order data has been added to the handler")
    assert existing_orders == processed_orders


def test_add_invalid_processed_orders():
    GIVEN("a handler and a set of valid processed orders")
    handler = OrdersHandler(bank=100000000000)
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
    handler.add_processed_orders(orders=processed_orders)
    existing_orders = handler._get_existing_orders()
    THEN("no order data has been added to the handler")
    assert existing_orders == []


def test_add_mixed_processed_orders():
    GIVEN("a handler and a set of processed orders (2 valid, 1 invalid)")
    handler = OrdersHandler(bank=100000000000)
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
    handler.add_processed_orders(orders=processed_orders)
    existing_orders = handler._get_existing_orders()
    THEN("the correct number of orders have been added to the handler")
    assert len(existing_orders) == 2
    THEN("the correct order data has been added to the handler")
    assert existing_orders == processed_orders[0:2]
