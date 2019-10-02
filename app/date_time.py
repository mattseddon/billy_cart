from datetime import datetime, timedelta
from dateutil import tz


class DateTime:
    utc_api_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    utc_format = "%Y-%m-%dT%H:%M:%SZ"
    time_format = "%H:%M:%S"
    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("Australia/Sydney")

    def __init__(self,str):
        self.__date_time = DateTime.__convert_from_utc_api_string(str)

    @staticmethod
    def utc_5_minutes_from_now():
        return DateTime.__utc_minutes_from_now(5)

    def is_more_than_33_seconds_from_now(self):
        is_more_than = (
            True
            if self.__date_time
            > DateTime.__add_time_to(date_time=DateTime.__get_utc_now(), seconds=33)
            else False
        )
        return is_more_than

    def local_hms_45_seconds_before(self):
        return self.__local_hms_seconds_before(seconds=45)

    def local_hms_30_seconds_before(self):
        return self.__local_hms_seconds_before(seconds=30)

    @staticmethod
    def get_utc_now():
        date_time_now = DateTime.__get_utc_now()
        date_time_now_str = DateTime.__convert_to_utc_string(date_time_now)
        return date_time_now_str

    @staticmethod
    def __get_utc_now():
        return datetime.utcnow()

    @staticmethod
    def __utc_minutes_from_now(from_now):
        date_time = DateTime.__add_time_to(
            date_time=DateTime.__get_utc_now(), minutes=from_now
        )
        date_time_str = DateTime.__convert_to_utc_string(date_time)
        return date_time_str

    def __local_hms_seconds_before(self, seconds):
        local_date_time = DateTime.__convert_timezone_to_local(date_time=self.__date_time)
        adjusted_date_time = DateTime.__add_time_to(date_time=local_date_time, seconds=-seconds)
        hour_minute_str = DateTime.__convert_to_hms_string(date_time=adjusted_date_time)
        return hour_minute_str

    @staticmethod
    def __add_time_to(date_time, minutes=0, seconds=0):
        date_time = date_time + timedelta(minutes=minutes,seconds=seconds)
        return date_time

    @staticmethod
    def __convert_from_utc_string(str):
        return DateTime.__convert_from_string(str=str, format=DateTime.utc_format)

    @staticmethod
    def __convert_from_utc_api_string(str):
        return DateTime.__convert_from_string(str=str, format=DateTime.utc_api_format)

    @staticmethod
    def __convert_from_string(str, format):
        return datetime.strptime(str, format)

    @staticmethod
    def __convert_to_utc_string(date_time):
        return DateTime.__convert_to_string(date_time=date_time, format=DateTime.utc_format)

    @staticmethod
    def __convert_to_hms_string(date_time):
        return DateTime.__convert_to_string(date_time=date_time, format=DateTime.time_format)

    @staticmethod
    def __convert_to_string(date_time, format):
        return date_time.strftime(format)

    @staticmethod
    def __convert_timezone_to_local(date_time):
        return date_time.replace(tzinfo=DateTime.from_zone).astimezone(DateTime.to_zone)
