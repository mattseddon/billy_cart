from app.third_party_adapter.date_time import DateTime
from numpy import nan


class RecordHandler:
    def __init__(self, record):
        self.__record = record

        self.id = self.__record.get("selectionId")
        self.__set_removal_date()
        self.__set_starting_prices()
        self.__set_exchange_prices()

    def is_valid(self):
        return True if self.id else False

    def __set_starting_prices(self):
        self.__sp = self.__set_value_or_default(value=self.__record.get("sp"))

        self.__set_sp_back()
        self.__set_sp_back_taken()

        self.__set_sp_lay()
        self.__set_sp_lay_taken()

    def __set_exchange_prices(self):
        self.__ex = self.__set_value_or_default(value=self.__record.get("ex"))
        self.__set_traded_volume()

        self.__set_total_back_price()
        self.__set_total_back_size()
        self.__set_average_back_price()

        self.__set_offered_back_odds()

        self.__set_total_lay_price()
        self.__set_total_lay_size()
        self.__set_average_lay_price()

        self.__set_offered_lay_odds()

    def __set_removal_date(self):
        removal_date = self.__record.get("removalDate")
        self.removal_date = DateTime(removal_date).get_epoch() if removal_date else nan
        return None

    def __set_sp_back(self):
        price = self.__sp.get("nearPrice")
        self.sp_back = price if self.__is_valid(price) else nan
        return None

    def __set_sp_back_taken(self):
        back_taken = self.__set_value_or_default(
            value=self.__sp.get("backStakeTaken"), default=[]
        )
        self.sp_back_taken = sum(price.get("size") for price in back_taken)
        return None

    def __set_sp_lay(self):
        self.sp_lay = self.__calc_lay_price(self.sp_back)

    def __set_sp_lay_taken(self):
        lay_taken = self.__set_value_or_default(
            value=self.__sp.get("layLiabilityTaken"), default=[]
        )
        self.sp_lay_taken = sum(price.get("size") for price in lay_taken)
        return None

    def __set_offered_back_odds(self):
        available_to_back = self.__ex.get("availableToBack")
        self.offered_back_odds = (
            available_to_back[0].get("price") if available_to_back else nan
        )
        return None

    def __set_offered_lay_odds(self):
        available_to_lay = self.__ex.get("availableToLay")
        self.offered_lay_odds = (
            available_to_lay[0].get("price") if available_to_lay else nan
        )
        return None

    def __set_traded_volume(self):
        traded_volume = self.__ex.get("tradedVolume") if self.__ex else None
        self.__traded_volume = self.__set_value_or_default(
            value=traded_volume, default=[]
        )
        return None

    def __set_total_back_price(self):
        self.__total_back_price = sum(
            trade.get("size") * trade.get("price") for trade in self.__traded_volume
        )
        return None

    def __set_total_back_size(self):
        self.total_back_size = sum(trade.get("size") for trade in self.__traded_volume)
        return None

    def __set_average_back_price(self):
        self.average_back_price = (
            self.__total_back_price / self.total_back_size
            if self.total_back_size
            else nan
        )
        return None

    def __set_total_lay_price(self):
        self.__total_lay_price = sum(
            trade.get("size")
            * (trade.get("price") - 1)
            * self.__calc_lay_price(trade.get("price"))
            for trade in self.__traded_volume
        )
        return None

    def __set_total_lay_size(self):
        self.total_lay_size = sum(
            trade.get("size") * (trade.get("price") - 1)
            for trade in self.__traded_volume
        )
        return None

    def __set_average_lay_price(self):
        self.average_lay_price = (
            self.__total_lay_price / self.total_lay_size if self.total_lay_size else nan
        )
        return None

    def __set_value_or_default(self, value, default={}):
        return value if value else default

    def __calc_lay_price(self, price):
        return 1 / (1 - (1 / price)) if self.__is_valid(price) else nan

    def __is_valid(self, price):
        return True if type(price) is float and price > 0 else False
