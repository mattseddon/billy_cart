from tests.utils import GIVEN, WHEN, THEN, almost_equal
from infrastructure.third_party.adapter.numpy_utils import (
    is_not_a_number,
    not_a_number,
    calculate_log,
    not_a_number_to_number,
)


def test_nan():
    GIVEN("a value that is not a number")
    nan = not_a_number()
    WHEN("we check if the value is not a number")
    true = is_not_a_number(nan)
    THEN("it is")
    assert true


def test_not_nan():
    GIVEN("a value that is a number")
    number = 1
    WHEN("we check if the value is not a number")
    true = is_not_a_number(number)
    THEN("it is not")
    assert not (true)


def test_nan_to_num():
    GIVEN("a value that is not a number")
    nan = not_a_number()
    WHEN("we convert the value to a number")
    number = not_a_number_to_number(nan)
    THEN("it is now the number 0")
    assert number == 0


def test_log():
    GIVEN("a list of values")
    approx_e = 2.71828182846
    values = [
        approx_e ** 0,
        approx_e ** 1,
        approx_e ** 2,
        approx_e ** 3,
        approx_e ** 4,
        approx_e ** 5,
    ]
    WHEN("we calculate the log for each value in the list")
    for i, value in enumerate(values):
        assert almost_equal(calculate_log(value), i)
