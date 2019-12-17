from tests.utils import GIVEN, WHEN, THEN
from app.market.data.utils import is_a_number, try_divide
from infrastructure.third_party.adapter.numpy_utils import not_a_number, is_not_a_number


def test_number_number():
    GIVEN("a number")
    x = 1
    WHEN("we test if it is a number")
    true = is_a_number(x)
    THEN("it is")
    assert true


def test_number_nan():
    GIVEN("a NaN value")
    nan = not_a_number()
    WHEN("we test if it is a number")
    true = is_a_number(nan)
    THEN("it is not")
    assert not (true)


def test_number_str():
    GIVEN("a string")
    str = "this is a string and not a number"
    WHEN("we test if it is a number")
    true = is_a_number(str)
    THEN("it is not")
    assert not (true)


def test_number_list():
    GIVEN("a list")
    l = [1, 2, 3, 4]
    WHEN("we test if it is a number")
    true = is_a_number(l)
    THEN("it is not")
    assert not (true)


def test_number_dict():
    GIVEN("a dictionary")
    d = {"a": 1, "b": 2, "c": 3}
    WHEN("we test if it is a number")
    true = is_a_number(d)
    THEN("it is not")
    assert not (true)

    GIVEN("a numeric only dictionary")
    d = {1: 1, 2: 2, 3: 3}
    WHEN("we test if it is a number")
    true = is_a_number(d)
    THEN("it is not")
    assert not (true)


def test_number_none():
    GIVEN("a None value")
    none = None
    WHEN("we test if it is a number")
    true = is_a_number(none)
    THEN("it is not")
    assert not (true)


def test_try_divide_number():
    GIVEN("a numerator and a divisor")
    numerator = 1
    denominator = 2
    WHEN("we try to divide")
    result = try_divide(value=numerator, by=denominator)
    THEN("the result is as expected")
    assert result == 0.5


def test_try_divide_nan():
    GIVEN("a numerator, a divisor and a NaN value")
    numerator = 1
    denominator = 2
    nan = not_a_number()

    WHEN("we try to divide the numerator by NaN")
    result = try_divide(value=numerator, by=nan)
    THEN("the result is as expected")
    assert is_not_a_number(result)

    WHEN("we try to divide NaN by the denominator")
    result = try_divide(value=nan, by=denominator)
    THEN("the result is as expected")
    assert is_not_a_number(result)

    WHEN("we try to divide NaN by NaN")
    result = try_divide(value=nan, by=nan)
    THEN("the result is as expected")
    assert is_not_a_number(result)


def test_try_divide_zero():
    GIVEN("a numerator and an invalid divisor")
    numerator = 1
    denominator = 0
    WHEN("we try to divide the numerator by NaN")
    result = try_divide(value=numerator, by=denominator)
    THEN("the result is as expected")
    assert is_not_a_number(result)
