from tests.utils import GIVEN, WHEN, THEN
from infrastructure.external_api.market.record.interface import ItemAdapterInterface
from pytest import fail, raises


def test_item_adapter_interface():
    GIVEN("the external api market interface")
    with raises(TypeError):
        WHEN(
            "a class inherits the interface but does not implement the appropriate method"
        )

        class DoesNotImplement(ItemAdapterInterface):
            pass

        THEN("an error is thrown on instantiation")
        DoesNotImplement()

    WHEN("a class inherits the interface and implements the appropriate method")

    class Implements(ItemAdapterInterface):
        def get_adapted_data(self):
            pass

    try:
        THEN("the class can be instantiated without error")
        Implements()
    except TypeError:
        fail("Unexpected TypeError")
