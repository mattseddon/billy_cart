from tests.utils import GIVEN, WHEN, THEN, almost_equal
from infrastructure.third_party.adapter.numpy_utils import not_a_number, is_not_a_number
from infrastructure.built_in.adapter.copy_utils import make_copy
from app.market.data.transform.handler import TransformHandler
from app.market.data.transform.price.handler import PriceHandler


def test_no_items():
    GIVEN("a transform handler")
    handler = TransformHandler()
    WHEN("we call process with no data")
    transformed_data = handler.process()
    THEN("an empty dictionary is returned")
    assert not transformed_data


def test_simple_comp_data():
    GIVEN("a simple set of data and a data transform handler")
    items = (
        {"id": 123, "sp_back_price": 2.1},
        {"id": 456, "sp_back_price": 2.1},
    )
    handler = TransformHandler()
    handler._set_items(items=items)
    WHEN("we calculate the compositional data")
    compositional_data = handler._get_compositional_data(price_name="sp_back_price")
    THEN("a list of dictionaries with the correct values is returned")
    assert compositional_data == [
        {"id": 123, "compositional_probability": 0.5, "compositional_price": 2},
        {"id": 456, "compositional_probability": 0.5, "compositional_price": 2},
    ]


def test_nan_comp_data():
    GIVEN("a simple set of data and a data transform handler")
    nan = not_a_number()
    items = (
        {"id": 123, "price": 0.476190476190476},
        {"id": 456, "price": 0.476190476190476},
        {"id": 789, "price": nan},
    )
    handler = TransformHandler()
    handler._set_items(items=items)

    WHEN("we calculate the compositional data")
    compositional_data = handler._get_compositional_data(price_name="price")
    THEN("a list of dictionaries with the correct values is returned")
    assert compositional_data[0:2] == [
        {"id": 123, "compositional_probability": 0.5, "compositional_price": 2},
        {"id": 456, "compositional_probability": 0.5, "compositional_price": 2},
    ]
    nan_entry = compositional_data[2]
    assert nan_entry.get("id") == 789
    assert is_not_a_number(nan_entry.get("compositional_probability"))
    assert is_not_a_number(nan_entry.get("compositional_price"))


def test_real_comp_data():
    GIVEN("a set of real life prices and a data transform handler")
    correct_probability = 1
    items = [
        {"id": 123, "price": 28.0},
        {"id": 223, "price": 120.0},
        {"id": 323, "price": 30.0},
        {"id": 423, "price": 9.1},
        {"id": 523, "price": 17.2},
        {"id": 623, "price": 72.0},
        {"id": 723, "price": 38.5},
        {"id": 823, "price": 52.5},
        {"id": 923, "price": 6.0},
        {"id": 113, "price": 15.0},
        {"id": 213, "price": 4.5},
        {"id": 313, "price": 285.0},
        {"id": 413, "price": 5.6},
        {"id": 513, "price": 34.5},
    ]

    handler = TransformHandler(total_probability=correct_probability)
    handler._set_items(items=items)

    expected_data = __calc_compositional_data(
        items=items, correct_probability=correct_probability
    )

    WHEN("we calculate the compositional data")
    compositional_data = handler._get_compositional_data(price_name="price")

    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_data):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_data[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_data),
        correct_probability,
    )


def test_item_removed_comp_data():
    GIVEN("a set of real life prices (with one removed) and a probability handler")
    correct_probability = 1 - (1 / 9.1)  # removed 9.1 price
    items = [
        {"id": 123, "price": 28.0},
        {"id": 223, "price": 120.0},
        {"id": 323, "price": 30.0},
        {"id": 523, "price": 17.2},
        {"id": 623, "price": 72.0},
        {"id": 723, "price": 38.5},
        {"id": 823, "price": 52.5},
        {"id": 923, "price": 6.0},
        {"id": 113, "price": 15.0},
        {"id": 213, "price": 4.5},
        {"id": 313, "price": 285.0},
        {"id": 413, "price": 5.6},
        {"id": 513, "price": 34.5},
    ]

    handler = TransformHandler(total_probability=correct_probability)
    handler._set_items(items=items)

    expected_data = __calc_compositional_data(
        items=items, correct_probability=correct_probability
    )

    WHEN("we calculate the compositional data")
    compositional_data = handler._get_compositional_data(price_name="price")

    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_data):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_data[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_data),
        correct_probability,
    )


def test_items_excluded_comp_data():
    GIVEN(
        "a set of real life prices, a data transform handler and two items to exclude from the list"
    )
    total_probability = 1
    items_to_exclude = [
        {"id": 123, "probability": 0.04},
        {"id": 223, "probability": 0.008},
    ]
    correct_probability = total_probability - sum(
        item.get("probability") for item in items_to_exclude
    )
    items = [
        {"id": 123, "price": 28.0},
        {"id": 223, "price": 120.0},
        {"id": 323, "price": 30.0},
        {"id": 423, "price": 9.1},
        {"id": 523, "price": 17.2},
        {"id": 623, "price": 72.0},
        {"id": 723, "price": 38.5},
        {"id": 823, "price": 52.5},
        {"id": 923, "price": 6.0},
        {"id": 113, "price": 15.0},
        {"id": 213, "price": 4.5},
        {"id": 313, "price": 285.0},
        {"id": 413, "price": 5.6},
        {"id": 513, "price": 34.5},
    ]

    handler = TransformHandler(total_probability=total_probability)
    WHEN("we exclude two of the items and calculate the compositional data")

    item_ids_to_exclude = []
    for item in items_to_exclude:
        runner_id = item.get("id")
        handler.set_probability(
            runner_id=runner_id, probability=item.get("probability")
        )
        item_ids_to_exclude.append(runner_id)
    handler._set_items(items=items)
    handler._calc_remaining_probability()
    expected_data = __calc_compositional_data(
        items=list(
            filter(lambda item: item.get("id") not in item_ids_to_exclude, items)
        ),
        correct_probability=correct_probability,
    )

    compositional_data = handler._get_compositional_data(price_name="price")

    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_data):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_data[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_data),
        correct_probability,
    )


def __calc_compositional_data(items, correct_probability):
    expected_data = make_copy(items)
    pricer = PriceHandler()
    total_probability = 0

    for item in expected_data:
        item["probability"] = pricer.calc_discounted_probability(item.get("price"))
        total_probability += item.get("probability")

    for item in expected_data:
        compositional_probability = (
            correct_probability / total_probability
        ) * item.get("probability")
        item["compositional_probability"] = compositional_probability
        item["compositional_price"] = pricer.calc_price(compositional_probability)

    return expected_data
