from tests.utils import GIVEN, WHEN, THEN, should_test_real_api
from app.api_handler import APIHandler
from private.details import get_user_details, get_cert, get_app_key
from unittest.mock import patch, MagicMock, Mock
from app.third_party_adapter.date_time import DateTime
from app.third_party_adapter.json_utils import make_json
from urllib.error import URLError


if should_test_real_api():

    def test_get_account_status():

        GIVEN("an API handler connected to the dev environment")
        dev_api_handler = APIHandler(environment="Dev")

        WHEN("we get the account status from the API")
        account_status = dev_api_handler.get_account_status()

        THEN("a dictionary is returned")
        assert type(account_status) is dict

        THEN(
            "the returned dict contains a bank variable which is a number greater than 0"
        )
        bank = account_status.get("availableToBetBalance")
        assert type(bank) is float
        assert bank > 0

        THEN(
            "the returned dict contains a discount rate to be applied which is a float greater than or equal to 0"
        )
        discount_rate = account_status.get("discountRate") / 100
        assert type(discount_rate) is float
        assert discount_rate >= 0

        THEN(
            "the returned dict contains a points value which is an int greater than or equal to 0"
        )
        points = account_status.get("pointsBalance")
        assert type(points) is int
        assert points >= 0

    def test_api_handler():

        GIVEN("an API handler connected to the dev environment")
        dev_api_handler = APIHandler(environment="Dev")

        WHEN("we get the markets which start in the next 5 minutes from the API")
        markets = dev_api_handler.get_markets("7", DateTime.utc_5_minutes_from_now())

        THEN("a list is returned")
        assert type(markets) is list

        THEN("each item in the list is a dict refering to a market")
        for market in markets:
            assert type(market) is dict

            THEN("each market has an id which is a string")
            market_id = market.get("marketId")
            assert type(market_id) is str

            THEN("each market has a name")
            assert type(market.get("marketName")) is str

            THEN("each market is associated with an event which is stored as a dict")
            event = market.get("event")
            assert type(event) is dict

            THEN("the event has an id which is a string")
            assert type(event.get("id")) is str

            THEN("the event has a name which is a string")
            assert type(event.get("name")) is str

            THEN("the event has a country code which is a string")
            assert type(event.get("countryCode")) is str

            WHEN("we get the market information from the API")
            market_info = dev_api_handler.get_market(market_id)

            THEN("a dict is returned")
            assert type(market_info) is dict
            if market_info:
                THEN("the dict contains a list of runners")
                assert type(market_info.get("runners")) is list

    def test_api_is_singleton():
        GIVEN("an API handler connected to the dev environment")
        dev_api_handler = APIHandler(environment="Dev")

        WHEN("we create a duplicate handler")
        duplicate_api_handler = APIHandler(environment="Dev")

        THEN("the duplicate handler is the same instance as the original")
        assert dev_api_handler is duplicate_api_handler

        THEN("both handlers have the same headers")
        assert dev_api_handler.headers == duplicate_api_handler.headers

        WHEN("we request a new set of headers")
        original_headers = dev_api_handler.headers
        duplicate_api_handler.set_headers()

        THEN("the handlers headers have changed")
        assert original_headers != dev_api_handler.headers

        THEN("both handlers still have the same headers")
        assert dev_api_handler.headers == duplicate_api_handler.headers


@patch("app.api_handler.post_request")
def test_set_headers(mock_post):
    GIVEN("we cannot connect to the dev environment")
    mock_post.return_value = {}

    WHEN("we try to instantiate the handler")
    dev_api_handler = APIHandler(environment="Dev")

    THEN("there are no headers in the handler")
    assert hasattr(dev_api_handler, "headers") is False

    WHEN("we try to set the headers manually")
    return_value = dev_api_handler.set_headers()

    THEN("the are still no headers in the handler")
    assert return_value == 0
    assert hasattr(dev_api_handler, "headers") is False


@patch.object(APIHandler, "set_headers")
@patch("app.api_handler.urlopen")
def test_error_handling(mock_urlopen, mock_set_headers):
    GIVEN("a mocked instance of the APIHandler")
    mock_set_headers.side_effect = setattr(APIHandler, "headers", {})
    dev_api_handler = APIHandler(environment="Dev")

    WHEN(
        "we try to get the markets which start in the next 5 minutes from the API but no payload is returned"
    )
    context_manager = MagicMock()
    context_manager.getcode.return_value = 200
    context_manager.read.return_value = make_json({})
    mock_urlopen.return_value = context_manager
    markets = dev_api_handler.get_markets("7", DateTime.utc_5_minutes_from_now())

    THEN("no information is returned from the handler")
    assert markets is None

    WHEN(
        "we try to get the markets which start in the next 5 minutes from the API but it throws an error"
    )
    mock_urlopen.side_effect = URLError(Mock(status=500), "I died, wwwaaaahhhhhhh")
    markets = dev_api_handler.get_markets("7", DateTime.utc_5_minutes_from_now())

    THEN("no information is returned from the handler")
    assert markets is None
