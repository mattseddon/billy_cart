from tests.utils import GIVEN, WHEN, THEN
from app.market.data.transform.handler import TransformHandler


def test_no_items():
    GIVEN("a transform handler")
    handler = TransformHandler()
    WHEN("we call process with no items")
    transformed_data = handler.process()
    THEN("an empty dictionary is returned")
    assert transformed_data == {}
