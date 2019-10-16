from tests.utils import GIVEN, WHEN, THEN
from third_party_adapters.api_utils import post_request

def test_post_request():
    GIVEN("a url")
    url = 'https://httpbin.org/post'
    WHEN("we send a post request")
    data = post_request(url=url)
    THEN("we get a response")
    assert type(data) is dict
    assert data.get("status_code") == 200