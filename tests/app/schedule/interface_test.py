from tests.utils import GIVEN, WHEN, THEN
from app.schedule.interface import ExternalAPIScheduleInterface
from pytest import fail, raises


def test_scheduler_interface():
    GIVEN("the external api schedule interface")
    with raises(TypeError):
        WHEN(
            "a class inherits the interface but does not implement the appropriate method"
        )

        class DoesNotImplement(ExternalAPIScheduleInterface):
            pass

        THEN("an error is thrown on instantiation")
        DoesNotImplement()

    WHEN("a class inherits the interface and implements the appropriate method")

    class Implements(ExternalAPIScheduleInterface):
        def get_schedule(self):
            pass

    try:
        THEN("the class can be instantiated without error")
        Implements()
    except TypeError:
        fail("Unexpected TypeError")
