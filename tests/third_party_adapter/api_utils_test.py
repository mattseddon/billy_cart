from tests.utils import GIVEN, WHEN, THEN, should_test_real_api
from app.third_party_adapter.api_utils import post_request

if should_test_real_api():

    def test_post_request():
        GIVEN("a url")
        url = "https://httpbin.org/post"
        WHEN("we send a post request")
        data = post_request(url=url)
        THEN("we get a response")
        assert type(data) is dict
        assert data.get("status_code") == 200
