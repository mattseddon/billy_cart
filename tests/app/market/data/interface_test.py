from tests.utils import GIVEN, WHEN, THEN
from app.market.data.interface import (
    ExternalAPIMarketDataInterface,
    DataContainerInterface,
)
from pytest import fail, raises


def test_market_data_external_api_interface():
    GIVEN("the external api market interface")
    with raises(TypeError):
        WHEN(
            "a class inherits the interface but does not implement the appropriate method"
        )

        class DoesNotImplement(ExternalAPIMarketDataInterface):
            pass

        THEN("an error is thrown on instantiation")
        DoesNotImplement()

    WHEN("a class inherits the interface and implements the appropriate method")

    class Implements(ExternalAPIMarketDataInterface):
        def convert(self):
            pass

    try:
        THEN("the class can be instantiated without error")
        Implements()
    except TypeError:
        fail("Unexpected TypeError")


def test_market_data_container_interface():
    GIVEN("the external api market interface")
    with raises(TypeError):
        WHEN(
            "a class inherits the interface but does not implement the appropriate method"
        )

        class DoesNotImplement(DataContainerInterface):
            pass

        THEN("an error is thrown on instantiation")
        DoesNotImplement()

    WHEN("a class inherits the interface and implements the appropriate method")

    class Implements(DataContainerInterface):
        def new(self):
            pass

        def add_rows(self):
            pass

        def get_row_count(self):
            pass

        def get_column_count(self):
            pass

        def get_column(self):
            pass

        def get_last_column_entry(self):
            pass

        def has_column(self):
            pass

        def get_column_group_values(self):
            pass

        def get_index(self):
            pass

        def set_index(self):
            pass

        def set_column_group_name(self):
            pass

    try:
        THEN("the class can be instantiated without error")
        Implements()
    except TypeError:
        fail("Unexpected TypeError")

