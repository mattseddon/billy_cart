from tests.utils import GIVEN, WHEN, THEN
from app.market.interface import ExternalAPIMarketInterface
from pytest import fail, raises


def test_market_interface():
    GIVEN("the external api market interface")
    with raises(TypeError):
        WHEN(
            "a class inherits the interface but does not implement the appropriate method"
        )

        class DoesNotImplement(ExternalAPIMarketInterface):
            pass

        THEN("an error is thrown on instantiation")
        DoesNotImplement()

    WHEN("a class inherits the interface and implements the appropriate method")

    class Implements(ExternalAPIMarketInterface):
        def get_market(self):
            pass

        def post_order(self):
            pass

    try:
        THEN("the class can be instantiated without error")
        Implements()
    except TypeError:
        fail("Unexpected TypeError")
