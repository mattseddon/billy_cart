from numpy import isnan, nan, log, nan_to_num, floor


def calculate_log(expression):
    return log(expression)


def not_a_number():
    return nan


def is_not_a_number(var):
    return isnan(var) if var else False


def not_a_number_to_number(var):
    return nan_to_num(var)


def make_native_type(value):
    return value if type(value) is str else value.item()


def round_down(value):
    return floor(value)
