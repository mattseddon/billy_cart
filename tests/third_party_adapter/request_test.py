from tests.utils import GIVEN, WHEN, THEN, should_test_real_api
from unittest.mock import patch, MagicMock, Mock
from app.third_party_adapter.request import post_data, open_url, _get_ok_status
from app.third_party_adapter.json_utils import make_json
from urllib.error import URLError

if should_test_real_api():

    def test_post_data():
        GIVEN("a url")
        url = "https://httpbin.org/post"
        WHEN("we send a post request")
        data = post_data(url=url)
        THEN("we get a response")
        assert type(data) is dict
        assert data.get("status_code") == _get_ok_status()

    def test_open_url():
        GIVEN("a url")
        url = "https://httpbin.org/anything"
        WHEN("we open the url")
        data = open_url(url=url,request='some form data')
        THEN("we get a response")
        assert type(data) is dict
        assert data.get("status_code") == _get_ok_status()


@patch("app.third_party_adapter.request.urlopen")
def test_error_handling(mock_urlopen):
    GIVEN("a url")
    url = "https://fakeurlrequests.io"
    WHEN(
        "we make a url request but an empty dictionary is returned"
    )
    context_manager = MagicMock()
    context_manager.getcode.return_value = _get_ok_status()
    context_manager.read.return_value = make_json({})
    mock_urlopen.return_value = context_manager
    dict = open_url(url=url,request='some form data')

    THEN("a dictionary containing status_code : 200 is returned")
    assert dict == {"status_code" : _get_ok_status() }

    WHEN(
        "we make a url request and an error is thrown"
    )
    mock_urlopen.side_effect = URLError(Mock(status=500), "I died, wwwaaaahhhhhhh")
    none = open_url(url=url,request='some form data')

    THEN("no information is returned")
    assert none is None