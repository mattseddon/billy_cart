from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.market.adapter.record import RecordAdapter

def test_empty_input():
    GIVEN("a empty input dictionary and a record adapter")
    input = {}
    adapter = RecordAdapter()
    WHEN("we convert the input")
    none = adapter.convert(input)
    THEN("None is returned")
    assert none is None

def test_missing_market_info():
    GIVEN("a empty input dictionary and a record adapter")
    input = { "marketStartTime": "2019-01-13T05:25:00.000Z", "et": "2019-01-13T05:20:04Z", "marketId": "1.153509934"}
    adapter = RecordAdapter()
    WHEN("we convert the input")
    none = adapter.convert(input)
    THEN("None is returned")
    assert none is None

