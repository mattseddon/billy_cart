from tests.utils import GIVEN, WHEN, THEN
from infrastructure.built_in.adapter.re_utils import regex_match


def test_regex_match():
    GIVEN("a pattern and a string that match")
    a_str = "This is a string"
    pattern = r"This\sis"
    WHEN("we call regex_match")
    return_str = regex_match(pattern=pattern, str=a_str)
    THEN("the string is returned")
    assert return_str == a_str

    GIVEN("a pattern and a string that do not match")
    a_str = "This is a string"
    pattern = r"This\sisnt"
    WHEN("we call regex_match")
    return_str = regex_match(pattern=pattern, str=a_str)
    THEN("the string is returned")
    assert return_str is None

    GIVEN("a date pattern and a string that match")
    a_str = "1984-11-07T12:45:00Z"
    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
    WHEN("we call regex_match")
    return_str = regex_match(pattern=pattern, str=a_str)
    THEN("the string is returned")
    assert return_str == a_str

    GIVEN("a different date pattern and a string that match")
    a_str = "1984-11-07T12:45:00.000Z"
    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"
    WHEN("we call regex_match")
    return_str = regex_match(pattern=pattern, str=a_str)
    THEN("the string is returned")
    assert return_str == a_str
