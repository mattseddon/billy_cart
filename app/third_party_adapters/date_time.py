from datetime import datetime, timedelta
from dateutil import tz
from app.third_party_adapters.re_utils import regex_match

class DateTime:
    __utc_format = "%Y-%m-%dT%H:%M:%SZ"
    __utc_api_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    __time_format = "%H:%M:%S"
    __from_zone = tz.gettz("UTC")
    __to_zone = tz.gettz("Australia/Sydney")

    def __init__(self,str):
        self.__str = str
        self.__utc_api_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"
        self.__date_time = self.__make_datetime()

    def get_epoch(self):
        return self.__date_time.timestamp()

    @staticmethod
    def utc_5_minutes_from_now():
        return DateTime.__utc_minutes_from_now(minutes=5)

    def is_more_than_33_seconds_from_now(self):
        is_more_than = (
            True
            if self.__date_time
            > DateTime.__add_to(date_time=DateTime.__get_utc_now(), seconds=33)
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
        date_time_now_str = DateTime.__convert_to_utc_string(date_time=date_time_now)
        return date_time_now_str

    def __make_datetime(self):
        if regex_match(pattern=self.__utc_api_pattern,str=self.__str):
            date_time = self.__convert_from_utc_api_string()
        else: 
            date_time = self.__convert_from_utc_string()
        return date_time

    @staticmethod
    def __utc_minutes_from_now(minutes):
        date_time = DateTime.__add_to(
            date_time=DateTime.__get_utc_now(), minutes=minutes
        )
        date_time_str = DateTime.__convert_to_utc_string(date_time=date_time)
        return date_time_str

    @staticmethod
    def __get_utc_now():
        return datetime.utcnow()

    def __local_hms_seconds_before(self, seconds):
        self.__convert_timezone_to_local()
        self.__add_to_date_time(seconds=-seconds)
        hour_minutes_str = self.__convert_to_hms_string()
        return hour_minutes_str

    def __add_to_date_time(self, minutes=0, seconds=0):
        self.__date_time = DateTime.__add_to(date_time=self.__date_time, minutes=minutes, seconds=seconds)

    @staticmethod
    def __add_to(date_time, minutes=0, seconds=0):
        date_time = date_time + timedelta(minutes=minutes,seconds=seconds)
        return date_time

    def __convert_from_utc_string(self):
        return self.__convert_from_string(format=DateTime.__utc_format)

    def __convert_from_utc_api_string(self):
        return self.__convert_from_string(format=DateTime.__utc_api_format)

    def __convert_from_string(self, format):
        return datetime.strptime(self.__str, format)

    @staticmethod
    def __convert_to_utc_string(date_time):
        return DateTime.__convert_to_string(date_time=date_time, format=DateTime.__utc_format)

    def __convert_to_hms_string(self):
        return DateTime.__convert_to_string(date_time=self.__date_time, format=DateTime.__time_format)

    @staticmethod
    def __convert_to_string(date_time, format):
        return date_time.strftime(format)

    def __convert_timezone_to_local(self):
        self.__date_time = self.__date_time.replace(tzinfo=DateTime.__from_zone).astimezone(DateTime.__to_zone)
