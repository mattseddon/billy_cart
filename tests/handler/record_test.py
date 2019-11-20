from tests.utils import GIVEN, WHEN, THEN
from app.handler.record import RecordHandler
from math import isnan


def test_create_record():

    GIVEN("an empty dictionary")
    data = {}
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    assert record.is_valid() is False
    __test_sp_defaults(record=record, data=data)
    __test_ex_defaults(record=record, data=data)
    assert isnan(record.removal_date)
    

    GIVEN("a dictionary with the correct information")
    data = __get_data()
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct information")
    assert record.id == __get_id(data)
    __test_sp_values(record, data)
    __test_ex_values(record, data)
    assert isnan(record.removal_date)

    GIVEN("a dictionary which has an empty sp attribute")
    data = __get_data(sp={})
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    __test_sp_defaults(record=record, data=data)
    __test_ex_values(record=record, data=data)

    GIVEN("a dictionary which is missing the sp attribute")
    data = __get_data()
    del data["sp"]
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    __test_sp_defaults(record=record, data=data)
    __test_ex_values(record=record, data=data)

    GIVEN("a dictionary which has an empty ex attribute")
    data = __get_data(ex={})
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    __test_ex_defaults(record=record, data=data)
    __test_sp_values(record=record, data=data)

    GIVEN("a dictionary which has an empty ex attribute")
    data = __get_data()
    del data['ex']
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    __test_ex_defaults(record=record, data=data)
    __test_sp_values(record=record, data=data)

    GIVEN("a dictionary which is missing the nearprice attribute")
    WHEN("we instantiate the record handler object")
    THEN("the object has all of the correct defaults applied")


def __test_sp_values(record, data):
    assert record.sp_back == __get_sp_back(data)
    assert record.sp_back_taken == __calc_sp_back_taken(data)
    assert record.sp_lay == __calc_lay_odds(__get_sp_back(data))
    assert record.sp_lay_taken == __calc_sp_lay_taken(data)

def __test_sp_defaults(record, data):
    assert record.id == __get_id(data)
    assert isnan(record.sp_back)
    assert record.sp_back_taken == 0
    assert isnan(record.sp_lay)
    assert record.sp_lay_taken == 0


def __test_ex_values(record, data):
    assert record.average_back_price == __calc_average_back_price(data)
    assert record.total_back_size == __calc_total_back_size(data)
    assert record.average_lay_price == __calc_average_lay_price(data)
    assert record.total_lay_size == __calc_total_lay_size(data)
    assert record.offered_back_odds == __get_offered_back_odds(data)
    assert record.offered_lay_odds == __get_offered_lay_odds(data)

def __test_ex_defaults(record,data):
    assert isnan(record.average_back_price)
    assert record.total_back_size == 0
    assert isnan(record.average_lay_price)
    assert record.total_lay_size == 0
    assert isnan(record.offered_back_odds)
    assert isnan(record.offered_lay_odds)


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


def __get_id(data):
    return data.get("selectionId")


def __get_sp_back(data):
    return data.get("sp").get("nearPrice")


def __calc_sp_back_taken(data):
    return sum(price.get("size") for price in data.get("sp").get("backStakeTaken"))


def __calc_lay_odds(odds):
    return 1 / (1 - (1 / odds))


def __calc_sp_lay_taken(data):
    return sum(price.get("size") for price in data.get("sp").get("layLiabilityTaken"))


def __calc_average_back_price(data):
    return sum(
        price.get("size") * price.get("price")
        for price in data.get("ex").get("tradedVolume")
    ) / __calc_total_back_size(data)


def __calc_total_back_size(data):
    return sum(price.get("size") for price in data.get("ex").get("tradedVolume"))


def __calc_average_lay_price(data):
    return sum(
        price.get("size")
        * (price.get("price") - 1)
        * (1 / (1 - (1 / price.get("price"))))
        for price in data.get("ex").get("tradedVolume")
    ) / __calc_total_lay_size(data)


def __calc_total_lay_size(data):
    return sum(
        price.get("size") * (price.get("price") - 1)
        for price in data.get("ex").get("tradedVolume")
    )


def __get_offered_back_odds(data):
    return data.get("ex").get("availableToBack")[0].get("price")


def __get_offered_lay_odds(data):
    return data.get("ex").get("availableToLay")[0].get("price")
