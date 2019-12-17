from infrastructure.third_party.adapter.numpy_utils import is_not_a_number, not_a_number


def is_a_number(value):
    return type(value) in [int, float, complex] and not (is_not_a_number(value))


def try_divide(value, by):
    return value / by if is_a_number(value) and __can_divide(by) else not_a_number()


def __can_divide(value):
    return value and is_a_number(value)
