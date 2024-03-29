from freezegun import freeze_time

from tests.utils import GIVEN, WHEN, THEN
from infrastructure.built_in.adapter.date_time import DateTime


@freeze_time("1984-11-07 12:45:00")
def test_datetime_helpers():
    GIVEN("the time has been overridden")

    WHEN("we call get_utc_now")
    now = DateTime.get_utc_now()
    THEN("the correct string is returned")
    assert now == "1984-11-07T12:45:00Z"

    WHEN("we call utc_5_minutes_from_now and add 5 minutes")
    five_minutes_from_now = DateTime.utc_5_minutes_from_now()
    THEN("the correct string is returned")
    assert five_minutes_from_now == "1984-11-07T12:50:00Z"

    WHEN("we call utc_15_minutes_from_now and add 5 minutes")
    five_minutes_from_now = DateTime.utc_15_minutes_from_now()
    THEN("the correct string is returned")
    assert five_minutes_from_now == "1984-11-07T13:00:00Z"

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time in the distant future"
    )
    is_future = DateTime("2019-01-01T00:00:00.000Z").is_more_than_33_seconds_from_now()
    THEN("the date time is far enough in the future to return true")
    assert is_future is True

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time 34 seconds in the future"
    )
    is_not_future = DateTime(
        "1984-11-07T12:45:34.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is far enough in the future to return true")
    assert is_not_future is True

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time 33 seconds in the future"
    )
    is_not_future = DateTime(
        "1984-11-07T12:44:33.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future is False

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time that matches our override"
    )
    is_not_future = DateTime(
        "1984-11-07T12:45:00.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future is False

    WHEN("we call is_datetime_more_than_33_seconds_from_now with a time from the past")
    is_not_future = DateTime(
        "1984-11-07T12:44:00.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future is False


def test_date_time_str_converters():
    GIVEN("a UTC date time string with milliseconds")
    utc_date_time_str = "2019-01-01T00:00:00.000Z"

    WHEN("we call local_hms_45_seconds_before")
    hour_minutes_seconds_str = DateTime(utc_date_time_str).local_hms_45_seconds_before()
    THEN(
        "a string in the correct format corresponding to the local date time is returned"
    )
    assert hour_minutes_seconds_str == "10:59:15"

    WHEN("we call utc_30_seconds_before")
    hour_minutes_seconds_str = DateTime(utc_date_time_str).local_hms_30_seconds_before()
    THEN(
        "a string in the correct format corresponding to the local date time is returned"
    )
    assert hour_minutes_seconds_str == "10:59:30"

    GIVEN("a UTC date time string without milliseconds")
    utc_date_time_str = "2019-01-01T12:00:00Z"

    WHEN("we call local_hms_45_seconds_before")
    hour_minutes_seconds_str = DateTime(utc_date_time_str).local_hms_45_seconds_before()
    THEN(
        "a string in the correct format corresponding to the local date time is returned"
    )
    assert hour_minutes_seconds_str == "22:59:15"

    WHEN("we call utc_30_seconds_before")
    hour_minutes_seconds_str = DateTime(utc_date_time_str).local_hms_30_seconds_before()
    THEN(
        "a string in the correct format corresponding to the local date time is returned"
    )
    assert hour_minutes_seconds_str == "22:59:30"


def test_date_time_epoch():
    GIVEN("a UTC date time string with milliseconds")
    utc_date_time_str = "2019-01-01T00:00:00.000Z"
    WHEN("we get the epoch representation")
    epoch = DateTime(utc_date_time_str).get_epoch()
    THEN("the correct epoch is returned")
    local_epoch = 1546261200
    assert epoch == local_epoch

    GIVEN("a UTC date time string and another that is 60 seconds afterwards")
    first_date_time_str = "2019-01-01T00:00:00.000Z"
    second_date_time_str = "2019-01-01T00:01:00.000Z"
    WHEN("we create instances of DateTime and subtract the epochs from one another")
    seconds_difference = (
        DateTime(first_date_time_str).get_epoch()
        - DateTime(second_date_time_str).get_epoch()
    )
    THEN("the difference is as expected")
    assert seconds_difference == -60

    GIVEN("a UTC date time strings")
    utc_date_time_str = "2019-01-01T00:00:00.000Z"
    WHEN("we create instances of DateTime and subtract the epochs from one another")
    seconds_difference = (
        DateTime(utc_date_time_str).get_epoch()
        - DateTime(utc_date_time_str).get_epoch()
    )
    THEN("there is no difference")
    assert seconds_difference == 0

    GIVEN("two UTC date time strings 60 seconds apart")
    first_date_time_str = "2019-01-01T00:01:00.000Z"
    second_date_time_str = "2019-01-01T00:00:00.000Z"
    WHEN("we create instances of DateTime and subtract the epochs from one another")
    seconds_difference = (
        DateTime(first_date_time_str).get_epoch()
        - DateTime(second_date_time_str).get_epoch()
    )
    THEN("the difference is as expected")
    assert seconds_difference == 60

    GIVEN("two milliseconds since epoch 1 second apart")
    first_epoch = 1569876588922
    second_epoch = 1569876587922
    WHEN("we create instances of DateTime and subtract the epochs from one another")
    seconds_difference = (
        DateTime(first_epoch).get_epoch() - DateTime(second_epoch).get_epoch()
    )
    THEN("the difference is as expected")
    assert seconds_difference == 1
