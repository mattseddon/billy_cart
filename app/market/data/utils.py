from infrastructure.third_party.adapter.numpy_utils import is_not_a_number, not_a_number


def calc_inverse_price(price):
    return 1 / (1 - (1 / price)) if is_valid_price(price) else not_a_number()


def calc_sell_liability(size, price):
    return size * (price - 1) if is_valid_price(price) and is_valid_size(size) else 0


def is_valid_price(price):
    return __is_valid(value=price, min_value=1)


def is_valid_size(size):
    return __is_valid(value=size)


def is_a_number(value):
    return type(value) in [int, float, complex] and not is_not_a_number(value)


def try_divide(value, denominator):
    return (
        value / denominator
        if is_a_number(value) and __can_divide(denominator)
        else not_a_number()
    )


def __is_valid(value, min_value=0):
    return bool(is_a_number(value) and value > min_value)


def __can_divide(value):
    return value and is_a_number(value)
