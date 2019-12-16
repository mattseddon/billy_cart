from numpy import isnan, nan, log, nan_to_num


def calculate_log(expression):
    return log(expression)


def not_a_number():
    return nan


def is_not_a_number(var):
    return isnan(var)


def not_a_number_to_number(var):
    return nan_to_num(var)
