from unittest.mock import patch

from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.market.record.item.adapter import ItemAdapter
from infrastructure.third_party.adapter.numpy_utils import is_not_a_number
from app.market.metadata.handler import MetadataHandler


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_create_item(required_variables):
    GIVEN("a dictionary with the correct information")
    item_data = __get_data()
    required_variables.return_value = all_variables
    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()

    THEN("the object has all of the correct information")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_sp_values(adapted_item_data=adapted_item_data, item_data=item_data)
    __test_ex_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_empty_input(required_variables):
    GIVEN("an empty dictionary")
    item_data = {}
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()

    THEN("the object has all of the correct defaults applied")
    assert not adapted_item_data


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_empty_sp(required_variables):
    GIVEN("a dictionary which has an empty sp attribute")
    item_data = __get_data(sp={})
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()

    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_sp_defaults(adapted_item_data=adapted_item_data, item_data=item_data)
    __test_ex_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_missing_sp(required_variables):
    GIVEN("a dictionary which is missing the sp attribute")
    item_data = __get_data()
    required_variables.return_value = all_variables

    del item_data["sp"]
    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()
    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_sp_defaults(adapted_item_data=adapted_item_data, item_data=item_data)
    __test_ex_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_invalid_near_price(required_variables):
    GIVEN("a dictionary which has Infinity in place of the nearPrice")
    item_data = __get_data(sp=__get_inf_sp())
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()
    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_sp_defaults(adapted_item_data=adapted_item_data, item_data=item_data)
    __test_ex_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_empty_ex(required_variables):
    GIVEN("a dictionary which has an empty ex attribute")
    item_data = __get_data(ex={})
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()
    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_ex_defaults(adapted_item_data=adapted_item_data)
    __test_sp_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_missing_ex(required_variables):
    GIVEN("a dictionary which is missing the ex attribute")
    item_data = __get_data()
    del item_data["ex"]
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()
    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_ex_defaults(adapted_item_data=adapted_item_data)
    __test_sp_values(adapted_item_data=adapted_item_data, item_data=item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_removed(required_variables):
    GIVEN("a dictionary representing a removed runner")
    item_data = __get_removed()
    required_variables.return_value = all_variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()
    THEN("the object has all of the correct defaults applied")
    assert adapted_item_data.get("id") == __get_id(item_data)
    __test_ex_defaults(adapted_item_data=adapted_item_data)
    __test_sp_defaults(adapted_item_data=adapted_item_data, item_data=item_data)
    THEN("the object has a removal_date")
    assert adapted_item_data.get("removal_date") > 0


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_reduced_metadata(required_variables):
    GIVEN("a dictionary with the correct information")
    item_data = __get_data()
    required_variables.return_value = ["id", "sp_back_size", "removal_date"]

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()

    THEN("the object has all of the correct information")
    assert adapted_item_data.get("id") == __get_id(item_data)
    assert adapted_item_data.get("sp_back_size") == __calc_sp_back_size(item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))
    assert len(adapted_item_data.keys()) == 3


@patch(
    "infrastructure.external_api.market.record.item.adapter.MetadataHandler.get_required_variables"
)
def test_buy_metadata(required_variables):
    GIVEN("a dictionary with the correct information")
    item_data = __get_data()
    variables = [
        "id",
        "removal_date",
        "sp_back_size",
        "ex_back_size",
        "sp_back_price",
        "ex_average_back_price",
        "ex_offered_back_price",
    ]
    required_variables.return_value = variables

    WHEN("we instantiate the item handler object")
    adapted_item_data = ItemAdapter(item_data).get_adapted_data()

    THEN("the object has all of the correct information")
    assert adapted_item_data.get("id") == __get_id(item_data)
    assert is_not_a_number(adapted_item_data.get("removal_date"))
    assert adapted_item_data.get("sp_back_size") == __calc_sp_back_size(item_data)
    assert adapted_item_data.get("ex_back_size") == __calc_ex_back_size(item_data)
    assert adapted_item_data.get("sp_back_price") == __get_sp_back_price(item_data)
    assert adapted_item_data.get(
        "ex_average_back_price"
    ) == __calc_ex_average_back_price(item_data)
    assert adapted_item_data.get(
        "ex_offered_back_price"
    ) == __get_ex_offered_back_price(item_data)
    assert len(adapted_item_data.keys()) == len(variables)


def __test_sp_values(adapted_item_data, item_data):
    assert adapted_item_data.get("sp_back_price") == __get_sp_back_price(item_data)
    assert adapted_item_data.get("sp_back_size") == __calc_sp_back_size(item_data)
    assert adapted_item_data.get("sp_lay_price") == __calc_lay_price(
        __get_sp_back_price(item_data)
    )
    assert adapted_item_data.get("sp_lay_size") == __calc_sp_lay_size(item_data)


def __test_sp_defaults(adapted_item_data, item_data):
    assert adapted_item_data.get("id") == __get_id(item_data)
    assert is_not_a_number(adapted_item_data.get("sp_back_price"))
    assert adapted_item_data.get("sp_back_size") == 0
    assert is_not_a_number(adapted_item_data.get("sp_lay_price"))
    assert adapted_item_data.get("sp_lay_size") == 0


def __test_ex_values(adapted_item_data, item_data):
    assert adapted_item_data.get(
        "ex_average_back_price"
    ) == __calc_ex_average_back_price(item_data)
    assert adapted_item_data.get("ex_back_size") == __calc_ex_back_size(item_data)
    assert adapted_item_data.get("ex_average_lay_price") == __calc_ex_average_lay_price(
        item_data
    )
    assert adapted_item_data.get("ex_lay_size") == __calc_lay_size(item_data)
    assert adapted_item_data.get(
        "ex_offered_back_price"
    ) == __get_ex_offered_back_price(item_data)
    assert adapted_item_data.get("ex_offered_lay_price") == __get_ex_offered_lay_price(
        item_data
    )


def __test_ex_defaults(adapted_item_data):
    assert is_not_a_number(adapted_item_data.get("ex_average_back_price"))
    assert adapted_item_data.get("ex_back_size") == 0
    assert is_not_a_number(adapted_item_data.get("ex_average_lay_price"))
    assert adapted_item_data.get("ex_lay_size") == 0
    assert is_not_a_number(adapted_item_data.get("ex_offered_back_price"))
    assert is_not_a_number(adapted_item_data.get("ex_offered_lay_price"))


def __get_sp_data():
    return {
        "nearPrice": 4.606127794,
        "backStakeTaken": [
            {"price": 1.01, "size": 558.56},
            {"price": 5.8, "size": 20.0},
        ],
        "farPrice": 1.1181607315366695,
        "layLiabilityTaken": [{"price": 1000.0, "size": 66.0}],
    }


def __get_ex_data():
    return {
        "availableToBack": [
            {"price": 6.0, "size": 33.55},
            {"price": 5.9, "size": 16.21},
            {"price": 5.7, "size": 9.22},
        ],
        "availableToLay": [
            {"price": 6.4, "size": 12.31},
            {"price": 6.6, "size": 5.8},
            {"price": 6.8, "size": 41.13},
        ],
        "tradedVolume": [
            {"price": 5.0, "size": 59.26},
            {"price": 5.2, "size": 3.02},
            {"price": 5.3, "size": 5.53},
            {"price": 5.5, "size": 162.58},
            {"price": 5.6, "size": 85.91},
            {"price": 5.7, "size": 104.11},
            {"price": 5.8, "size": 49.99},
            {"price": 5.9, "size": 88.78},
            {"price": 6.0, "size": 102.71},
            {"price": 6.2, "size": 118.01},
            {"price": 6.4, "size": 339.88},
            {"price": 6.6, "size": 161.27},
        ],
    }


def __get_inf_sp():
    return {
        "nearPrice": "Infinity",
        "backStakeTaken": [],
        "farPrice": "NaN",
        "layLiabilityTaken": [],
    }


def __get_data(sp=__get_sp_data(), ex=__get_ex_data()):
    return {
        "status": "ACTIVE",
        "handicap": 0.0,
        "selectionId": 11719985,
        "sp": sp,
        "totalMatched": 1281.05,
        "adjustmentFactor": 15.385,
        "ex": ex,
        "lastPriceTraded": 6.2,
    }


def __get_removed():
    return {
        "status": "REMOVED",
        "handicap": 0.0,
        "selectionId": 281358,
        "sp": {"backStakeTaken": [], "layLiabilityTaken": []},
        "removalDate": "2019-03-19T22:57:56.000Z",
        "adjustmentFactor": 19.623,
        "ex": {"availableToBack": [], "availableToLay": [], "tradedVolume": []},
    }


def __get_id(item_data):
    return item_data.get("selectionId")


def __get_sp_back_price(item_data):
    return item_data.get("sp").get("nearPrice")


def __calc_lay_price(price):
    return 1 / (1 - (1 / price))


def __calc_ex_average_back_price(item_data):
    return sum(
        price.get("size") * price.get("price")
        for price in __get_traded_volume(item_data)
    ) / __calc_ex_back_size(item_data)


def __calc_ex_back_size(item_data):
    return sum(price.get("size") for price in __get_traded_volume(item_data))


def __calc_ex_average_lay_price(item_data):
    return sum(
        price.get("size")
        * (price.get("price") - 1)
        * (1 / (1 - (1 / price.get("price"))))
        for price in __get_traded_volume(item_data)
    ) / __calc_lay_size(item_data)


def __calc_lay_size(item_data):
    return sum(
        price.get("size") * (price.get("price") - 1)
        for price in __get_traded_volume(item_data)
    )


def __get_traded_volume(item_data):
    ex = item_data.get("ex") if item_data.get("ex") else {}
    traded_volume = ex.get("tradedVolume") if ex.get("tradedVolume") else []
    return traded_volume


def __get_ex_offered_back_price(item_data):
    return item_data.get("ex").get("availableToBack")[0].get("price")


def __get_ex_offered_lay_price(item_data):
    return item_data.get("ex").get("availableToLay")[0].get("price")


def __calc_sp_back_size(item_data):
    return sum(price.get("size") for price in item_data.get("sp").get("backStakeTaken"))


def __calc_sp_lay_size(item_data):
    return sum(
        price.get("size") for price in item_data.get("sp").get("layLiabilityTaken")
    )


metadata = MetadataHandler()
all_variables = metadata.get_extended_variable_list()
