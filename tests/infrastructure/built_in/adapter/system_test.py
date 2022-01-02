from pytest import raises

from tests.utils import GIVEN, WHEN, THEN

from infrastructure.built_in.adapter.system import die


def test_die():

    GIVEN("we want the program to exit")

    WHEN("we call die")
    with raises(SystemExit) as system_exit:
        die()
    THEN("the program exits")
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 0
