from tests.utils import GIVEN, WHEN, THEN, almost_equal
from app.market.data.transform.probability.handler import ProbabilityHandler
from infrastructure.built_in.adapter.copy_utils import make_copy
from infrastructure.third_party.adapter.numpy_utils import not_a_number, is_not_a_number


def test_simple_comp_data():
    GIVEN("a simple set of data and a probability handler")
    items = (
        {"id": 123, "sp_probability": 0.476190476190476},
        {"id": 456, "sp_probability": 0.476190476190476},
    )
    handler = ProbabilityHandler(
        items=items, name="sp_probability", correct_probability=1
    )
    WHEN("we calculate the compositional probabilities")
    compositional_probabilities = handler.calc_compositional_probabilities()
    THEN("a list of dictionaries with the correct values is returned")
    assert compositional_probabilities == [
        {"id": 123, "compositional_probability": 0.5},
        {"id": 456, "compositional_probability": 0.5},
    ]


def test_nan_comp_data():
    GIVEN("a simple set of data and a probability handler")
    nan = not_a_number()
    items = (
        {"id": 123, "sp_probability": 0.476190476190476},
        {"id": 456, "sp_probability": 0.476190476190476},
        {"id": 789, "sp_probability": nan},
    )
    handler = ProbabilityHandler(
        items=items, name="sp_probability", correct_probability=1
    )
    WHEN("we calculate the compositional probabilities")
    compositional_probabilities = handler.calc_compositional_probabilities()
    THEN("a list of dictionaries with the correct values is returned")
    assert compositional_probabilities[0:2] == [
        {"id": 123, "compositional_probability": 0.5},
        {"id": 456, "compositional_probability": 0.5},
    ]
    nan_entry = compositional_probabilities[2]
    assert nan_entry.get("id") == 789
    assert is_not_a_number(nan_entry.get("compositional_probability"))


def test_real_comp_data():
    GIVEN("a set of real life prices and a probability handler")
    correct_probability = 1
    items = [
        {"id": 123, "probability": 0.035714285714286,},
        {"id": 223, "probability": 0.008333333333333},
        {"id": 323, "probability": 0.033333333333333},
        {"id": 423, "probability": 0.10989010989011},
        {"id": 523, "probability": 0.058126746109399},
        {"id": 623, "probability": 0.013888888888889},
        {"id": 723, "probability": 0.025974025974026},
        {"id": 823, "probability": 0.019047619047619},
        {"id": 923, "probability": 0.168067226890756},
        {"id": 113, "probability": 0.066777284297006},
        {"id": 213, "probability": 0.222222222222222},
        {"id": 313, "probability": 0.003508771929825},
        {"id": 413, "probability": 0.18018018018018},
        {"id": 513, "probability": 0.028985507246377},
    ]

    handler = ProbabilityHandler(
        items=items, name="probability", correct_probability=correct_probability
    )

    expected_items = __calc_compositional_probabilities(
        items=items, correct_probability=correct_probability
    )

    WHEN("we calculate the compositional probabilities")
    compositional_items = handler.calc_compositional_probabilities()
    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_items):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_items[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_items),
        correct_probability,
    )


def test_item_removed_comp_data():
    GIVEN("a set of real life prices (with one removed) and a probability handler")
    correct_probability = 1 - (0.10989010989011)  # removed 9.1 price
    items = [
        {"id": 123, "probability": 0.035714285714286},
        {"id": 223, "probability": 0.008333333333333},
        {"id": 323, "probability": 0.033333333333333},
        {"id": 523, "probability": 0.058126746109399},
        {"id": 623, "probability": 0.013888888888889},
        {"id": 723, "probability": 0.025974025974026},
        {"id": 823, "probability": 0.019047619047619},
        {"id": 923, "probability": 0.168067226890756},
        {"id": 113, "probability": 0.066777284297006},
        {"id": 213, "probability": 0.222222222222222},
        {"id": 313, "probability": 0.003508771929825},
        {"id": 413, "probability": 0.18018018018018},
        {"id": 513, "probability": 0.028985507246377},
    ]

    handler = ProbabilityHandler(
        items=items, name="probability", correct_probability=correct_probability
    )

    expected_items = __calc_compositional_probabilities(
        items=items, correct_probability=correct_probability
    )

    WHEN("we calculate the compositional probabilities")
    compositional_items = handler.calc_compositional_probabilities()
    THEN("a list of dictionaries with the correct values is returned")
    for idx, item in enumerate(compositional_items):
        for key in item.keys():
            assert almost_equal(item.get(key), expected_items[idx].get(key))
    assert almost_equal(
        sum(item.get("compositional_probability") for item in compositional_items),
        correct_probability,
    )


def __calc_compositional_probabilities(items, correct_probability):
    expected_items = make_copy(items)

    total_probability = 0
    for item in expected_items:
        total_probability += item["probability"]

    for item in expected_items:
        item["compositional_probability"] = (
            correct_probability / total_probability
        ) * item.get("probability")

    return expected_items
