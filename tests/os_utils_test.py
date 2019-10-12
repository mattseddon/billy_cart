from tests.utils import GIVEN, WHEN, THEN
from app.os_utils import get_environment_variable, set_environment_variable, path_exists


def test_get_environment_variable():
    GIVEN("a Test environment variable")
    variable = "Test"
    set_environment_variable(variable=variable, value="Pass")
    WHEN("we retrieve it")
    Test = get_environment_variable(variable=variable)
    THEN("the correct variable value is returned")
    assert Test == "Pass"

    GIVEN("no environment variable")
    WHEN("we retrieve it")
    Test = get_environment_variable(variable=" ")
    THEN("the correct variable value is returned")
    assert Test == None

def test_path_exists():
    GIVEN("a valid existing path")
    path = './'
    WHEN("we check to see if the path exists")
    exists = path_exists(path=path)
    THEN("it does")
    assert exists == True

    GIVEN("an invalid and non-existent path")
    path = './wwwwwwwweeeeeeeeeeeeee/wwwwweeeeeeeeeeee/wwwwwwwweeeeeeeee'
    WHEN("we check to see if the path exists")
    exists = path_exists(path=path)
    THEN("it does")
    assert exists == False