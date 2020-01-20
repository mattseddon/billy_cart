from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.market.record.adapter import (
    ExternalAPIMarketRecordAdapter,
)
from infrastructure.built_in.adapter.json_utils import make_dict
from pytest import mark


def test_empty_input():
    GIVEN("a empty input dictionary and a record adapter")
    input = {}
    adapter = ExternalAPIMarketRecordAdapter(
        market_start_time="2019-01-01T00:00:00.000Z"
    )

    WHEN("we convert the input")
    none = adapter.convert(input)

    THEN("None is returned")
    assert none is None


def test_missing_market_info():
    GIVEN("a empty input dictionary and a record adapter")
    input = {
        "process_time": "2019-01-13T05:20:04Z",
        "marketId": "1.153509934",
    }
    adapter = ExternalAPIMarketRecordAdapter(
        market_start_time="2019-01-13T05:25:00.000Z"
    )

    WHEN("we convert the input")
    none = adapter.convert(input)

    THEN("None is returned")
    assert none is None


def test_valid_record():
    GIVEN("a valid input dictionary and a record adapter")
    input = __get_data()
    adapter = ExternalAPIMarketRecordAdapter(
        market_start_time="2019-01-13T07:05:00.000Z"
    )

    WHEN("we convert the input")
    adapted_data = adapter.convert(input)
    number_items = len(input.get("runners"))

    THEN("the correct number of items are returned")
    assert len(adapted_data.get("items") or []) == number_items


def test_mostly_valid_record():

    GIVEN(
        "a mostly valid input dictionary (with two invalid items) and a record adapter"
    )
    input = __get_data()
    for i in range(2):
        del input["runners"][i]["selectionId"]
    adapter = ExternalAPIMarketRecordAdapter(
        market_start_time="2019-01-13T07:05:00.000Z"
    )

    WHEN("we convert the input")
    adapted_data = adapter.convert(input)
    number_items = len(input.get("runners")) - 2

    THEN("the correct number of items are returned")
    assert len(adapted_data.get("items") or []) == number_items


def __get_data():
    return make_dict(
        '{"runners": [{"status": "ACTIVE", "handicap": 0.0, "selectionId": 8724980, "sp": {"nearPrice": 28.0, "backStakeTaken": [{"price": 120.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 9.99, "adjustmentFactor": 4.545, "ex": {"availableToBack": [{"price": 17.5, "size": 6.94}, {"price": 15.0, "size": 9.66}, {"price": 14.0, "size": 122.08}], "availableToLay": [{"price": 40.0, "size": 6.36}, {"price": 70.0, "size": 9.17}, {"price": 75.0, "size": 5.0}], "tradedVolume": [{"price": 16.5, "size": 10.0}]}, "lastPriceTraded": 16.5}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 7406222, "sp": {"nearPrice": 120.0, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 0.498, "ex": {"availableToBack": [{"price": 80.0, "size": 7.69}, {"price": 75.0, "size": 5.0}, {"price": 50.0, "size": 9.52}], "availableToLay": [{"price": 350.0, "size": 6.33}, {"price": 400.0, "size": 8.52}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 2588927, "sp": {"nearPrice": 30.0, "backStakeTaken": [{"price": 120.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 39.99, "adjustmentFactor": 5.0, "ex": {"availableToBack": [{"price": 14.0, "size": 9.72}, {"price": 13.5, "size": 7.39}, {"price": 13.0, "size": 120.0}], "availableToLay": [{"price": 50.0, "size": 6.85}, {"price": 60.0, "size": 8.14}, {"price": 65.0, "size": 5.0}], "tradedVolume": [{"price": 14.5, "size": 30.81}, {"price": 15.0, "size": 6.92}, {"price": 15.5, "size": 1.99}, {"price": 16.0, "size": 0.28}]}, "lastPriceTraded": 14.5}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 7407243, "sp": {"nearPrice": 9.1, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 70.28, "adjustmentFactor": 10.0, "ex": {"availableToBack": [{"price": 7.2, "size": 6.65}, {"price": 6.6, "size": 8.23}, {"price": 6.4, "size": 120.0}], "availableToLay": [{"price": 11.0, "size": 6.34}, {"price": 12.0, "size": 10.47}, {"price": 18.5, "size": 16.85}], "tradedVolume": [{"price": 8.0, "size": 13.07}, {"price": 8.2, "size": 6.92}, {"price": 8.4, "size": 13.24}, {"price": 8.6, "size": 6.76}, {"price": 8.8, "size": 20.01}, {"price": 9.0, "size": 10.0}, {"price": 9.2, "size": 0.28}]}, "lastPriceTraded": 9.2}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 7338681, "sp": {"nearPrice": 17.20378426340816, "backStakeTaken": [{"price": 1.01, "size": 45.11}, {"price": 60.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 3.846, "ex": {"availableToBack": [{"price": 18.5, "size": 12.48}, {"price": 16.5, "size": 124.77}, {"price": 15.5, "size": 24.52}], "availableToLay": [{"price": 75.0, "size": 6.12}, {"price": 85.0, "size": 9.17}, {"price": 90.0, "size": 5.0}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 12743060, "sp": {"nearPrice": 72.0, "backStakeTaken": [{"price": 140.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 1.235, "ex": {"availableToBack": [{"price": 42.0, "size": 70.17}, {"price": 40.0, "size": 9.11}, {"price": 32.0, "size": 5.14}], "availableToLay": [{"price": 110.0, "size": 6.36}, {"price": 200.0, "size": 5.54}, {"price": 280.0, "size": 5.19}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 7978445, "sp": {"nearPrice": 38.5, "backStakeTaken": [{"price": 85.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 50.0, "adjustmentFactor": 2.174, "ex": {"availableToBack": [{"price": 28.0, "size": 6.96}, {"price": 24.0, "size": 124.71}, {"price": 21.0, "size": 17.56}], "availableToLay": [{"price": 55.0, "size": 11.23}, {"price": 110.0, "size": 5.34}, {"price": 180.0, "size": 9.07}], "tradedVolume": [{"price": 25.0, "size": 36.73}, {"price": 26.0, "size": 6.36}, {"price": 27.0, "size": 6.92}]}, "lastPriceTraded": 25.0}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 12649338, "sp": {"nearPrice": 52.5, "backStakeTaken": [{"price": 90.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 2.632, "ex": {"availableToBack": [{"price": 24.0, "size": 6.64}, {"price": 23.0, "size": 9.85}, {"price": 22.0, "size": 120.0}], "availableToLay": [{"price": 80.0, "size": 6.28}, {"price": 120.0, "size": 7.27}, {"price": 130.0, "size": 8.98}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 22361367, "sp": {"nearPrice": 5.95, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 10.19, "adjustmentFactor": 22.285, "ex": {"availableToBack": [{"price": 4.9, "size": 8.11}, {"price": 3.85, "size": 8.12}, {"price": 3.7, "size": 11.4}], "availableToLay": [{"price": 6.8, "size": 10.33}, {"price": 7.8, "size": 36.77}, {"price": 8.8, "size": 35.55}], "tradedVolume": [{"price": 5.7, "size": 10.2}]}, "lastPriceTraded": 5.7}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 20258183, "sp": {"nearPrice": 14.97515226214193, "backStakeTaken": [{"price": 1.01, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 5.0, "ex": {"availableToBack": [{"price": 14.5, "size": 7.52}, {"price": 14.0, "size": 6.54}, {"price": 12.0, "size": 125.6}], "availableToLay": [{"price": 36.0, "size": 7.36}, {"price": 50.0, "size": 7.08}, {"price": 55.0, "size": 14.92}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 17775017, "sp": {"nearPrice": 4.5, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 22.727, "ex": {"availableToBack": [{"price": 3.8, "size": 6.79}, {"price": 3.75, "size": 7.88}, {"price": 3.7, "size": 6.76}], "availableToLay": [{"price": 5.1, "size": 10.48}, {"price": 5.2, "size": 5.6}, {"price": 7.8, "size": 32.61}], "tradedVolume": []}}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 15708088, "sp": {"nearPrice": 285.0, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 0.38, "adjustmentFactor": 0.45, "ex": {"availableToBack": [{"price": 100.0, "size": 7.17}, {"price": 75.0, "size": 7.66}, {"price": 50.0, "size": 7.25}], "availableToLay": [{"price": 450.0, "size": 6.35}, {"price": 480.0, "size": 8.52}, {"price": 690.0, "size": 5.26}], "tradedVolume": [{"price": 150.0, "size": 0.38}]}, "lastPriceTraded": 150.0}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 22032700, "sp": {"nearPrice": 5.55, "backStakeTaken": [], "farPrice": "NaN", "layLiabilityTaken": []}, "totalMatched": 10.28, "adjustmentFactor": 16.667, "ex": {"availableToBack": [{"price": 4.9, "size": 8.7}, {"price": 4.8, "size": 35.34}, {"price": 4.6, "size": 8.03}], "availableToLay": [{"price": 6.0, "size": 9.46}, {"price": 6.2, "size": 7.88}, {"price": 9.8, "size": 5.4}], "tradedVolume": [{"price": 4.7, "size": 7.12}, {"price": 4.8, "size": 3.16}]}, "lastPriceTraded": 4.7}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 22361368, "sp": {"nearPrice": 34.5, "backStakeTaken": [{"price": 60.0, "size": 5.0}], "farPrice": 1.0, "layLiabilityTaken": []}, "totalMatched": 0.0, "adjustmentFactor": 2.941, "ex": {"availableToBack": [{"price": 21.0, "size": 9.56}, {"price": 20.0, "size": 5.88}, {"price": 19.5, "size": 123.46}], "availableToLay": [{"price": 48.0, "size": 6.36}, {"price": 75.0, "size": 5.34}, {"price": 90.0, "size": 11.14}], "tradedVolume": []}}], "process_time": "2019-01-13T07:00:34Z"}'
    )
