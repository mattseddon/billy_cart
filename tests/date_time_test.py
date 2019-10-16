from tests.utils import GIVEN, WHEN, THEN
from third_party_adapters.date_time import DateTime
from freezegun import freeze_time


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

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time in the distant future"
    )
    is_future = DateTime("2019-01-01T00:00:00.000Z").is_more_than_33_seconds_from_now()
    THEN("the date time is far enough in the future to return true")
    assert is_future == True

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time 34 seconds in the future"
    )
    is_not_future = DateTime(
        "1984-11-07T12:45:34.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is far enough in the future to return true")
    assert is_not_future == True

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time 33 seconds in the future"
    )
    is_not_future = DateTime(
        "1984-11-07T12:44:33.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future == False

    WHEN(
        "we call is_datetime_more_than_33_seconds_from_now with a time that matches our override"
    )
    is_not_future = DateTime(
        "1984-11-07T12:45:00.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future == False

    WHEN("we call is_datetime_more_than_33_seconds_from_now with a time from the past")
    is_not_future = DateTime(
        "1984-11-07T12:44:00.000Z"
    ).is_more_than_33_seconds_from_now()
    THEN("the date time is not far enough in the future to return true")
    assert is_not_future == False


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
