from app.third_party_adapter.date_time import DateTime
from numpy import nan, isnan


class ItemAdapter:
    def __init__(self, record):
        self.__record = record

        self.__id = self.__record.get("selectionId")
        self.__sp = self.__get_value_or_default(value=self.__record.get("sp"))
        self.__ex = self.__get_value_or_default(value=self.__record.get("ex"))
        self.__set_traded_volume()
        self.__set_total_back_size()
        self.__set_total_lay_size()
        self.__set_sp_back()
        self.__data = {
            "id": self.__id,
            "removal_date": self.__get_removal_date(),
            "sp_back": self.__sp_back,
            "sp_lay": self.__get_sp_lay(),
            "total_back_size": self.__total_back_size,
            "total_lay_size": self.__total_lay_size,
            "average_back_price": self.__calc_average_back_price(),
            "average_lay_price": self.__calc_average_lay_price(),
            "total_back_sp": self.__calc_total_back_sp(),
            "total_lay_sp": self.__calc_total_lay_sp(),
            "offered_back_price": self.__get_offered_back_price(),
            "offered_lay_price": self.__get_offered_lay_price(),
        }

    def get(self, key):
        return self.__data.get(key)

    def is_valid(self):
        return True if self.__id else False

    def __get_removal_date(self):
        raw_removal_date = self.__record.get("removalDate")
        removal_date = (
            DateTime(raw_removal_date).get_epoch() if raw_removal_date else nan
        )
        return removal_date

    def __set_sp_back(self):
        price = self.__sp.get("nearPrice")
        self.__sp_back = price if self.__is_valid(price) else nan
        return None

    def __get_sp_lay(self):
        sp_lay = self.__calc_lay_price(self.__sp_back)
        return sp_lay

    def __set_traded_volume(self):
        traded_volume = self.__ex.get("tradedVolume") if self.__ex else None
        self.__traded_volume = self.__get_value_or_default(
            value=traded_volume, default=[]
        )
        return None

    def __calc_average_back_price(self):
        total_back_price = sum(
            trade.get("size") * trade.get("price") for trade in self.__traded_volume
        )

        average_back_price = (
            total_back_price / self.__total_back_size if self.__total_back_size else nan
        )
        return average_back_price

    def __calc_average_lay_price(self):
        total_lay_price = sum(
            trade.get("size")
            * (trade.get("price") - 1)
            * self.__calc_lay_price(trade.get("price"))
            for trade in self.__traded_volume
        )

        average_lay_price = (
            total_lay_price / self.__total_lay_size if self.__total_lay_size else nan
        )
        return average_lay_price

    def __set_total_back_size(self):
        self.__total_back_size = sum(
            trade.get("size") for trade in self.__traded_volume
        )
        return None

    def __calc_total_back_sp(self):
        total_back_sp = (
            self.__total_back_size + self.__calc_sp_back_taken()
            if self.__is_valid(self.__sp_back)
            else 0
        )
        return total_back_sp

    def __calc_sp_back_taken(self):
        back_taken = self.__get_value_or_default(
            value=self.__sp.get("backStakeTaken"), default=[]
        )
        sp_back_taken = sum(price.get("size") for price in back_taken)
        return sp_back_taken

    def __set_total_lay_size(self):
        self.__total_lay_size = sum(
            trade.get("size") * (trade.get("price") - 1)
            for trade in self.__traded_volume
        )
        return None

    def __calc_total_lay_sp(self):
        total_lay_sp = (
            self.__total_lay_size + self.__calc_sp_lay_taken() * (self.__sp_back - 1)
            if self.__is_valid(self.__sp_back)
            else 0
        )
        return total_lay_sp

    def __calc_sp_lay_taken(self):
        lay_taken = self.__get_value_or_default(
            value=self.__sp.get("layLiabilityTaken"), default=[]
        )
        sp_lay_taken = sum(price.get("size") for price in lay_taken)
        return sp_lay_taken

    def __get_offered_back_price(self):
        available_to_back = self.__ex.get("availableToBack")
        offered_back_price = (
            available_to_back[0].get("price") if available_to_back else nan
        )
        return offered_back_price

    def __get_offered_lay_price(self):
        available_to_lay = self.__ex.get("availableToLay")
        offered_lay_price = (
            available_to_lay[0].get("price") if available_to_lay else nan
        )
        return offered_lay_price

    def __get_value_or_default(self, value, default={}):
        return value if value else default

    def __calc_lay_price(self, price):
        return 1 / (1 - (1 / price)) if self.__is_valid(price) else nan

    def __is_valid(self, price):
        return True if type(price) is float and price > 0 else False
