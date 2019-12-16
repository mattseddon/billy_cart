from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.market.adapter.item import ItemAdapter
from infrastructure.third_party.adapter.numpy_utils import is_not_a_number


def test_create_record():
    GIVEN("a dictionary with the correct information")
    data = __get_data()

    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)

    THEN("the object has all of the correct information")
    assert record.get("id") == __get_id(data)
    __test_sp_values(record, data)
    __test_ex_values(record, data)
    assert is_not_a_number(record.get("removal_date"))


def test_empty_input():
    GIVEN("an empty dictionary")
    data = {}

    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)

    THEN("the object has all of the correct defaults applied")
    assert record.is_valid() is False
    __test_sp_defaults(record=record, data=data)
    __test_ex_defaults(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_empty_sp():
    GIVEN("a dictionary which has an empty sp attribute")
    data = __get_data(sp={})

    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)

    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_sp_defaults(record=record, data=data)
    __test_ex_values(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_missing_sp():
    GIVEN("a dictionary which is missing the sp attribute")
    data = __get_data()
    del data["sp"]
    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)
    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_sp_defaults(record=record, data=data)
    __test_ex_values(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_invalid_near_price():
    GIVEN("a dictionary which has Infinity in place of the nearPrice")
    data = __get_data(sp=__get_inf_sp())
    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)
    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_sp_defaults(record=record, data=data)
    __test_ex_values(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_empty_ex():
    GIVEN("a dictionary which has an empty ex attribute")
    data = __get_data(ex={})
    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)
    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_ex_defaults(record=record, data=data)
    __test_sp_values(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_missing_ex():
    GIVEN("a dictionary which is missing the ex attribute")
    data = __get_data()
    del data["ex"]

    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)

    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_ex_defaults(record=record, data=data)
    __test_sp_values(record=record, data=data)
    assert is_not_a_number(record.get("removal_date"))


def test_removed():
    GIVEN("a dictionary representing a removed runner")
    data = __get_removed()

    WHEN("we instantiate the record handler object")
    record = ItemAdapter(data)

    THEN("the object has all of the correct defaults applied")
    assert record.get("id") == __get_id(data)
    __test_ex_defaults(record=record, data=data)
    __test_sp_defaults(record=record, data=data)
    THEN("the object has a removal_date")
    assert record.get("removal_date") > 0


def __test_sp_values(record, data):
    assert record.get("sp_back_price") == __get_sp_back(data)
    assert record.get("sp_back_size") == __calc_sp_back_size(data)
    assert record.get("sp_lay_price") == __calc_lay_price(__get_sp_back(data))
    assert record.get("sp_lay_size") == __calc_sp_lay_size(data)


def __test_sp_defaults(record, data):
    assert record.get("id") == __get_id(data)
    assert is_not_a_number(record.get("sp_back_price"))
    assert record.get("sp_back_size") == 0
    assert is_not_a_number(record.get("sp_lay_price"))
    assert record.get("sp_lay_size") == 0


def __test_ex_values(record, data):
    assert record.get("ex_average_back_price") == __calc_ex_average_back_price(data)
    assert record.get("ex_back_size") == __calc_back_size(data)
    assert record.get("ex_average_lay_price") == __calc_ex_average_lay_price(data)
    assert record.get("ex_lay_size") == __calc_lay_size(data)
    assert record.get("ex_offered_back_price") == __get_ex_offered_back_price(data)
    assert record.get("ex_offered_lay_price") == __get_ex_offered_lay_price(data)


def __test_ex_defaults(record, data):
    assert is_not_a_number(record.get("ex_average_back_price"))
    assert record.get("ex_back_size") == 0
    assert is_not_a_number(record.get("ex_average_lay_price"))
    assert record.get("ex_lay_size") == 0
    assert is_not_a_number(record.get("ex_offered_back_price"))
    assert is_not_a_number(record.get("ex_offered_lay_price"))


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


def __get_id(data):
    return data.get("selectionId")


def __get_sp_back(data):
    return data.get("sp").get("nearPrice")


def __calc_lay_price(price):
    return 1 / (1 - (1 / price))


def __calc_ex_average_back_price(data):
    return sum(
        price.get("size") * price.get("price") for price in __get_traded_volume(data)
    ) / __calc_back_size(data)


def __calc_back_size(data):
    return sum(price.get("size") for price in __get_traded_volume(data))


def __calc_ex_average_lay_price(data):
    return sum(
        price.get("size")
        * (price.get("price") - 1)
        * (1 / (1 - (1 / price.get("price"))))
        for price in __get_traded_volume(data)
    ) / __calc_lay_size(data)


def __calc_lay_size(data):
    return sum(
        price.get("size") * (price.get("price") - 1)
        for price in __get_traded_volume(data)
    )


def __get_traded_volume(data):
    ex = data.get("ex") if data.get("ex") else {}
    traded_volume = ex.get("tradedVolume") if ex.get("tradedVolume") else []
    return traded_volume


def __get_ex_offered_back_price(data):
    return data.get("ex").get("availableToBack")[0].get("price")


def __get_ex_offered_lay_price(data):
    return data.get("ex").get("availableToLay")[0].get("price")


def __calc_sp_back_size(data):
    return sum(price.get("size") for price in data.get("sp").get("backStakeTaken"))


def __calc_sp_lay_size(data):
    return sum(price.get("size") for price in data.get("sp").get("layLiabilityTaken"))
