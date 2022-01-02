from unittest.mock import patch
from pytest import mark

from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.schedule.handler import ExternalAPIScheduleHandler
from infrastructure.built_in.adapter.date_time import DateTime


@mark.slow
@mark.external
def test_get_account_status():

    GIVEN("a schedule handler connected to the dev environment")
    schedule_handler = ExternalAPIScheduleHandler(environment="Dev")

    WHEN("we get the account status")
    account_status = schedule_handler.get_account_status()

    THEN("a dictionary is returned")
    assert isinstance(account_status, dict)

    THEN("the returned dict contains a bank variable which is a number greater than 0")
    bank = account_status.get("availableToBetBalance")
    assert isinstance(bank, float)
    assert bank > 0

    THEN(
        "the returned dict contains a discount rate to be applied"
        + " which is a float greater than or equal to 0"
    )
    discount_rate = account_status.get("discountRate") / 100
    assert isinstance(discount_rate, float)
    assert discount_rate >= 0

    THEN(
        "the returned dict contains a points value which is an int greater than or equal to 0"
    )
    points = account_status.get("pointsBalance")
    assert isinstance(points, int)
    assert points >= 0


@mark.slow
@mark.external
def test_schedule_handler():

    GIVEN("a schedule handler connected to the dev environment")
    dev_schedule_handler = ExternalAPIScheduleHandler(environment="Dev")

    WHEN("we get the schedule for market which start in the next 5 minutes")
    schedule = dev_schedule_handler.get_schedule("7", DateTime.utc_5_minutes_from_now())

    THEN("a list is returned")
    assert isinstance(schedule, list)

    THEN("each item in the list is a dict refering to a market")
    for market in schedule:
        assert isinstance(market, dict)

        THEN("each market has an id which is a string")
        market_id = market.get("marketId")
        assert isinstance(market_id, str)

        THEN("each market has a name")
        assert isinstance(market.get("marketName"), str)

        THEN("each market is associated with an event which is stored as a dict")
        event = market.get("event")
        assert isinstance(event, dict)

        THEN("the event has an id which is a string")
        assert isinstance(event.get("id"), str)

        THEN("the event has a name which is a string")
        assert isinstance(event.get("name"), str)

        THEN("the event has a country code which is a string")
        assert isinstance(event.get("countryCode"), str)


@mark.slow
@mark.external
def test_object_is_singleton():
    GIVEN("a schedule handler connected to the dev environment")
    dev_schedule_handler = ExternalAPIScheduleHandler(environment="Dev")

    WHEN("we create a duplicate handler")
    duplicate_api_handler = ExternalAPIScheduleHandler(environment="Dev")

    THEN("the duplicate handler is the same instance as the original")
    assert dev_schedule_handler is duplicate_api_handler

    THEN("both handlers have the same headers")
    assert dev_schedule_handler.get_headers() == duplicate_api_handler.get_headers()

    WHEN("we request a new set of headers")
    original_headers = dev_schedule_handler.get_headers()
    duplicate_api_handler.set_headers()

    THEN("the handlers headers have changed")
    assert original_headers != dev_schedule_handler.get_headers()

    THEN("both handlers still have the same headers")
    assert dev_schedule_handler.get_headers() == duplicate_api_handler.get_headers()


@patch("infrastructure.external_api.handler.post_data")
def test_set_headers(mock_post):
    GIVEN("we cannot connect to the dev environment")
    mock_post.return_value = {}

    WHEN("we try to instantiate the schedule handler")
    dev_schedule_handler = ExternalAPIScheduleHandler(environment="Dev")

    THEN("there are no headers in the handler")
    assert dev_schedule_handler._headers is None

    WHEN("we try to set the headers manually")
    return_value = dev_schedule_handler.set_headers()

    THEN("the are still no headers in the handler")
    assert return_value == 0
    assert dev_schedule_handler._headers is None


@patch.object(ExternalAPIScheduleHandler, "set_headers")
@patch("infrastructure.external_api.handler.open_url")
def test_error_handling(mock_urlopen, mock_set_headers):
    GIVEN("a mocked instance of the ExternalAPIScheduleHandler")
    mock_set_headers.side_effect = setattr(ExternalAPIScheduleHandler, "_headers", {})
    dev_schedule_handler = ExternalAPIScheduleHandler(environment="Dev")

    WHEN(
        "we try to get the for all markets which start"
        + " in the next 5 minutes but no payload is returned"
    )
    mock_urlopen.return_value = {}
    schedule = dev_schedule_handler.get_schedule("7", DateTime.utc_5_minutes_from_now())

    THEN("no information is returned from the handler")
    assert schedule is None

    WHEN(
        "we try to get the markets which start in the next 5 minutes but it throws an error"
    )
    mock_urlopen.return_value = None
    schedule = dev_schedule_handler.get_schedule("7", DateTime.utc_5_minutes_from_now())

    THEN("no information is returned from the handler")
    assert schedule is None
