from urllib.error import URLError
from unittest.mock import patch, MagicMock, Mock
from pytest import mark


from tests.utils import GIVEN, WHEN, THEN
from infrastructure.built_in.adapter.request import (
    post_data,
    open_url,
    get_ok_status,
)
from infrastructure.built_in.adapter.json_utils import make_json


@mark.slow
@mark.external
def test_post_data():
    GIVEN("a url")
    url = "https://httpbin.org/post"
    WHEN("we send a post request")
    data = post_data(url=url)
    THEN("we get a response")
    isinstance(data, dict)
    assert data.get("status_code") == get_ok_status()


@mark.slow
@mark.external
def test_open_url():
    GIVEN("a url")
    url = "https://httpbin.org/anything"
    WHEN("we open the url")
    data = open_url(url=url, request="some form data")
    THEN("we get a response")
    isinstance(data, dict)
    assert data.get("status_code") == get_ok_status()


@patch("infrastructure.built_in.adapter.request.urlopen")
def test_error_handling(mock_urlopen):
    GIVEN("a url")
    url = "https://mockurlrequests.io"
    WHEN("we make a url request but an empty dictionary is returned")
    context_manager = MagicMock()
    context_manager.getcode.return_value = get_ok_status()
    context_manager.read.return_value = make_json({})
    mock_urlopen.return_value = context_manager
    data = open_url(url=url, request="some form data")

    THEN("a dictionary containing status_code : 200 is returned")
    assert data == {"status_code": get_ok_status()}

    WHEN("we make a url request and an error is thrown")
    mock_urlopen.side_effect = URLError(Mock(status=500), "I died, wwwaaaahhhhhhh")
    none = open_url(url=url, request="some form data")

    THEN("no information is returned")
    assert none is None
