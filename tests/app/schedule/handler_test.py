from app.market.handler import MarketHandler
from tests.utils import GIVEN, WHEN, THEN
from app.schedule.handler import ScheduleHandler
from infrastructure.external_api.schedule.handler import ExternalAPIScheduleHandler

from unittest.mock import patch


@patch.object(ExternalAPIScheduleHandler, "set_headers")
@patch.object(ExternalAPIScheduleHandler, "get_headers")
@patch("infrastructure.external_api.handler.ExternalAPIHandler._call_exchange")
def test_handler(mock_call_exchange, mock_get_headers, mock_set_headers):
    GIVEN("an External API schedule handler and a schedule handler")
    external_api = ExternalAPIScheduleHandler(environment="Dev")
    mock_call_exchange.return_value = __get_schedule()
    mock_get_headers.return_value = {}
    handler = ScheduleHandler(external_api=external_api)
    WHEN("we get the schedule")
    schedule = handler.get_schedule()
    THEN("the expected schedule is returned")
    assert schedule == __get_schedule()

    WHEN("we create market handlers for each of the markets in the schedule")
    new_markets = handler.create_new_markets(schedule)
    THEN("the new markets are in a list")
    assert type(new_markets) is list
    assert len(new_markets) == len(schedule)
    THEN("the market handlers have been created")
    for market in new_markets:
        assert type(market) is MarketHandler
        assert market.get_market_id() in [1.123456, 1.123457]


def __get_schedule():
    return [
        {
            "marketId": "1.123456",
            "event": {"countryCode": "AU"},
            "marketStartTime": "2020-02-05T02:35:00.000Z",
        },
        {
            "marketId": "1.123457",
            "event": {"countryCode": "AU"},
            "marketStartTime": "2020-02-05T02:30:00.000Z",
        },
    ]
