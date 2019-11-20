from tests.utils import GIVEN, WHEN, THEN
from app.handler.record import RecordHandler
from numpy import nan


def test_create_record():

    GIVEN("an empty dictionary")
    data = {}
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct defaults applied")
    assert record.is_valid() is False

    GIVEN("a dictionary with the correct information")
    data = __get_data()
    WHEN("we instantiate the record handler object")
    record = RecordHandler(data)
    THEN("the object has all of the correct information")
    assert record.id == data.get("selectionId")
    assert record.sp_back == data.get("sp").get("nearPrice")
    assert record.sp_back_taken == sum(
        price.get("size") for price in data.get("sp").get("backStakeTaken")
    )
    assert record.sp_lay == 1 / (1 - (1 / data.get("sp").get("nearPrice")))
    assert record.sp_lay_taken == sum(
        price.get("size") for price in data.get("sp").get("layLiabilityTaken")
    )
    assert record.tBP == sum(
        price.get("size") * price.get("price")
        for price in data.get("ex").get("tradedVolume")
    ) / sum(price.get("size") for price in data.get("ex").get("tradedVolume"))
    assert record.tBPd == sum(
        price.get("size") for price in data.get("ex").get("tradedVolume")
    )
    assert record.tLP == sum(
        price.get("size")
        * (price.get("price") - 1)
        * (1 / (1 - (1 / price.get("price"))))
        for price in data.get("ex").get("tradedVolume")
    ) / sum(
        price.get("size") * (price.get("price") - 1)
        for price in data.get("ex").get("tradedVolume")
    )
    assert record.tLPd == sum(
        price.get("size") * (price.get("price") - 1)
        for price in data.get("ex").get("tradedVolume")
    )
    assert record.offered_back_odds == data.get("ex").get("availableToBack")[0].get(
        "price"
    )
    assert record.offered_lay_odds == data.get("ex").get("availableToLay")[0].get(
        "price"
    )
    assert record.removal_date is nan

    GIVEN("a dictionary which is missing the sp attribute")
    WHEN("we instantiate the record handler object")
    THEN("the object has all of the correct defaults applied")

    GIVEN("a dictionary which is missing the ex attribute")
    WHEN("we instantiate the record handler object")
    THEN("the object has all of the correct defaults applied")

    GIVEN("a dictionary which is missing the nearprice attribute")
    WHEN("we instantiate the record handler object")
    THEN("the object has all of the correct defaults applied")


def __get_data():
    return {
        "status": "ACTIVE",
        "handicap": 0.0,
        "selectionId": 11719985,
        "sp": {
            "nearPrice": 4.606127794,
            "backStakeTaken": [
                {"price": 1.01, "size": 558.56},
                {"price": 5.8, "size": 20.0},
            ],
            "farPrice": 1.1181607315366695,
            "layLiabilityTaken": [{"price": 1000.0, "size": 66.0}],
        },
        "totalMatched": 1281.05,
        "adjustmentFactor": 15.385,
        "ex": {
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
        },
        "lastPriceTraded": 6.2,
    }
