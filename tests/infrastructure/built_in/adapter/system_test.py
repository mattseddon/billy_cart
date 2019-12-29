from tests.utils import GIVEN, WHEN, THEN

from infrastructure.built_in.adapter.system import die

from pytest import raises


def test_die():

    GIVEN("we want the program to exit")

    WHEN("we call die")
    with raises(SystemExit) as system_exit:
        die(0)
    THEN("the program exits")
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 0

