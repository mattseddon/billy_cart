from tests.utils import GIVEN, WHEN, THEN, almost_equal
from app.market.data.compositional_data.handler import CompositionalDataHandler
from infrastructure.built_in.adapter.copy_utils import make_copy


def test_simple_comp_data():
    GIVEN("a simple set of data and a compositional_data_handler")
    items = {"id": 123, "sp_back_price": 2.1}, {"id": 456, "sp_back_price": 2.1}
    handler = CompositionalDataHandler(
        items=items, price_name="sp_back_price", correct_probability=1
    )
    WHEN("we call calc_compositional_data")
    cdf = handler.calc_compositional_data()
    THEN("a list of dictionaries with the correct values is returned")
    assert cdf == [
        {
            "id": 123,
            "adj_price": (1.1 * 0.95) + 1,
            "probability": 1 / ((1.1 * 0.95) + 1),
            "compositional_probability": 0.5,
            "compositional_price": 2,
        },
        {
            "id": 456,
            "adj_price": (1.1 * 0.95) + 1,
            "probability": 1 / ((1.1 * 0.95) + 1),
            "compositional_probability": 0.5,
            "compositional_price": 2,
        },
    ]


def test_real_comp_data():
    GIVEN("a set of real life prices and a compositional_data_handler")
    correct_probability = 1
    items = [
        {"id": 123, "price": 28.0,},
        {"id": 223, "price": 120.0,},
        {"id": 323, "price": 30.0,},
        {"id": 423, "price": 9.1},
        {"id": 523, "price": 17.20378426340816,},
        {"id": 623, "price": 72.0},
        {"id": 723, "price": 38.5},
        {"id": 823, "price": 52.5},
        {"id": 923, "price": 5.95},
        {"id": 113, "price": 14.97515226214193},
        {"id": 213, "price": 4.5},
        {"id": 313, "price": 285.0},
        {"id": 413, "price": 5.55},
        {"id": 513, "price": 34.5},
    ]

    handler = CompositionalDataHandler(
        items=items, price_name="price", correct_probability=correct_probability
    )

    expected_items = __calc_compositional_data(
        items=items, correct_probability=correct_probability
    )

    WHEN("we call calc_compositional_data")
    compositional_items = handler.calc_compositional_data()
    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_items):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_items[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_items),
        correct_probability,
    )


def test_item_removed_comp_data():
    GIVEN(
        "a set of real life prices (with one removed) and a compositional_data_handler"
    )
    correct_probability = 1 - (1 / 9.1)  # removed 9.1 price
    items = [
        {"id": 123, "price": 28.0,},
        {"id": 223, "price": 120.0,},
        {"id": 323, "price": 30.0,},
        {"id": 523, "price": 17.20378426340816,},
        {"id": 623, "price": 72.0},
        {"id": 723, "price": 38.5},
        {"id": 823, "price": 52.5},
        {"id": 923, "price": 5.95},
        {"id": 113, "price": 14.97515226214193},
        {"id": 213, "price": 4.5},
        {"id": 313, "price": 285.0},
        {"id": 413, "price": 5.55},
        {"id": 513, "price": 34.5},
    ]

    handler = CompositionalDataHandler(
        items=items, price_name="price", correct_probability=correct_probability
    )

    expected_items = __calc_compositional_data(
        items=items, correct_probability=correct_probability
    )

    WHEN("we call calc_compositional_data")
    compositional_items = handler.calc_compositional_data()
    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_items):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_items[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_items),
        correct_probability,
    )


def __calc_compositional_data(items, correct_probability):
    expected_items = make_copy(items)

    total_probability = 0
    for item in expected_items:
        item["adj_price"] = 1 + ((item.get("price") - 1) * 0.95)
        del item["price"]
        item["probability"] = 1 / item.get("adj_price")
        total_probability += item["probability"]

    for item in expected_items:
        item["compositional_probability"] = (
            correct_probability / total_probability
        ) * item.get("probability")
        item["compositional_price"] = 1 / item["compositional_probability"]

    return expected_items
