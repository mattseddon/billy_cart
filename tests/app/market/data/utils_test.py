from tests.utils import GIVEN, WHEN, THEN
from app.market.data.utils import (
    calc_inverse_price,
    calc_sell_liability,
    is_a_number,
    is_valid_price,
    try_divide,
)
from infrastructure.third_party.adapter.numpy_utils import not_a_number, is_not_a_number


def test_number_number():
    GIVEN("a number")
    number = 1
    WHEN("we test if it is a number")
    true = is_a_number(number)
    THEN("it is")
    assert true


def test_number_nan():
    GIVEN("a NaN value")
    nan = not_a_number()
    WHEN("we test if it is a number")
    true = is_a_number(nan)
    THEN("it is not")
    assert not true


def test_number_str():
    GIVEN("a string")
    a_str = "this is a string and not a number"
    WHEN("we test if it is a number")
    true = is_a_number(a_str)
    THEN("it is not")
    assert not true


def test_number_list():
    GIVEN("a list")
    data = [1, 2, 3, 4]
    WHEN("we test if it is a number")
    true = is_a_number(data)
    THEN("it is not")
    assert not true


def test_number_dict():
    GIVEN("a dictionary")
    data = {"a": 1, "b": 2, "c": 3}
    WHEN("we test if it is a number")
    true = is_a_number(data)
    THEN("it is not")
    assert not true

    GIVEN("a numeric only dictionary")
    data = {1: 1, 2: 2, 3: 3}
    WHEN("we test if it is a number")
    true = is_a_number(data)
    THEN("it is not")
    assert not true


def test_number_none():
    GIVEN("a None value")
    none = None
    WHEN("we test if it is a number")
    true = is_a_number(none)
    THEN("it is not")
    assert not true


def test_try_divide_number():
    GIVEN("a numerator and a divisor")
    numerator = 1
    denominator = 2
    WHEN("we try to divide")
    result = try_divide(value=numerator, denominator=denominator)
    THEN("the result is as expected")
    assert result == 0.5


def test_try_divide_nan():
    GIVEN("a numerator, a divisor and a NaN value")
    numerator = 1
    denominator = 2
    nan = not_a_number()

    WHEN("we try to divide the numerator by NaN")
    result = try_divide(value=numerator, denominator=nan)
    THEN("the result is as expected")
    assert is_not_a_number(result)

    WHEN("we try to divide NaN by the denominator")
    result = try_divide(value=nan, denominator=denominator)
    THEN("the result is as expected")
    assert is_not_a_number(result)

    WHEN("we try to divide NaN by NaN")
    result = try_divide(value=nan, denominator=nan)
    THEN("the result is as expected")
    assert is_not_a_number(result)


def test_try_divide_zero():
    GIVEN("a numerator and an invalid divisor")
    numerator = 1
    denominator = 0
    WHEN("we try to divide the numerator by NaN")
    result = try_divide(value=numerator, denominator=denominator)
    THEN("the result is as expected")
    assert is_not_a_number(result)


def test_inverse_price():
    GIVEN("a price")
    buy_price = 2
    WHEN("we calculate the inverse")
    sell_price = calc_inverse_price(buy_price)
    THEN("the correct price is returned")
    assert sell_price == 2

    GIVEN("another valid price")
    buy_price = 1.5
    WHEN("we calculate the sell price")
    sell_price = calc_inverse_price(buy_price)
    THEN("the correct price is returned")
    assert sell_price == 1 / (1 - (1 / buy_price))

    GIVEN("a string price")
    buy_price = "a price"
    WHEN("we calculate the sell price")
    sell_price = calc_inverse_price(buy_price)
    THEN("the sell price is shown to be not a number")
    assert is_not_a_number(sell_price)

    GIVEN("a negative price")
    buy_price = -2
    WHEN("we calculate the sell price")
    sell_price = calc_inverse_price(buy_price)
    THEN("the sell price is shown to be not a number")
    assert is_not_a_number(sell_price)

    GIVEN("a price between 0 and 1")
    buy_price = 0.99
    WHEN("we calculate the sell price")
    sell_price = calc_inverse_price(buy_price)
    THEN("the sell price is shown to be not a number")
    assert is_not_a_number(sell_price)


def test_is_valid_price():
    GIVEN("a price")
    price = 1.01
    WHEN("we check if the price is valid")
    valid = is_valid_price(price)
    THEN("a true value is returned")
    assert valid

    GIVEN("an invalid price")
    price = 1
    WHEN("we check if the price is valid")
    valid = is_valid_price(price)
    THEN("a true value is returned")
    assert not (valid)


def test_calc_sell_liability():
    GIVEN("a price and a size")
    price = 1.01
    size = 100
    WHEN("we calculate the sell liability")
    liability = calc_sell_liability(price=price, size=size)
    THEN("the correct value is returned")
    assert liability == 100 * (1.01 - 1)

    GIVEN("an invalid price and a size")
    price = 0.99
    size = 1000000
    WHEN("we calculate the sell liability")
    liability = calc_sell_liability(price=price, size=size)
    THEN("the correct value is returned")
    assert liability == 0

    GIVEN("a price and an invalid size")
    price = 1.99
    size = -1
    WHEN("we calculate the sell liability")
    liability = calc_sell_liability(price=price, size=size)
    THEN("the correct value is returned")
    assert liability == 0

    GIVEN("an invalid price and an invalid size")
    price = 1
    size = -1
    WHEN("we calculate the sell liability")
    liability = calc_sell_liability(price=price, size=size)
    THEN("the correct value is returned")
    assert liability == 0
