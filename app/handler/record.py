from app.third_party_adapter.date_time import DateTime
from numpy import nan


class RecordHandler:
    def __init__(self, record):
        self.__record = record
        self.__extract_data()

    def is_valid(self):
        return True if self.id else False

    def __extract_data(self):

        self.__set_removal_date()
        self.id = self.__record.get("selectionId")

        self.__sp = self.__set_value_or_default(value=self.__record.get("sp"))
        self.__ex = self.__set_value_or_default(value=self.__record.get("ex"))

        self.__set_sp_back()

        back_taken = self.__set_value_or_default(
            value=self.__sp.get("backStakeTaken"), default=[]
        )
        self.sp_back_taken = 0
        for price in back_taken:
            self.sp_back_taken += price.get("size")

        lay_taken = self.__set_value_or_default(
            value=self.__sp.get("layLiabilityTaken"), default=[]
        )
        self.sp_lay_taken = 0
        for price in lay_taken:
            self.sp_lay_taken += price.get("size")

        self.sp_lay = self.__calc_lay_odds(self.sp_back)

        available_to_back = self.__ex.get("availableToBack")
        self.offered_back_odds = available_to_back[0].get("price") if available_to_back else nan

        available_to_lay = self.__ex.get("availableToLay")
        self.offered_lay_odds = available_to_lay[0].get("price") if available_to_lay else nan

        self.__set_traded_volume()
        self.__set_average_back_price()
        self.__set_average_lay_price()

    def __set_value_or_default(self, value, default={}):
        return value if value else default

    def __set_removal_date(self):
        removal_date = self.__record.get("removal_date")
        self.removal_date = DateTime(removal_date).get_epoch() if removal_date else nan
        return None

    def __set_sp_back(self):
        price = self.__sp.get("nearPrice")
        self.sp_back = price if self.__is_valid(price) else nan
        return None

    def __is_valid(self, price):
        return False if price in ["Infinity", "NaN", 0, None] else True

    def __calc_lay_odds(self, odds):
        """
        return the lay odds from the back odds
        """
        try:
            lay_odds = 1 / (1 - (1 / odds))
        except:
            lay_odds = nan

        return lay_odds

    def __set_traded_volume(self):
        traded_volume = self.__ex.get("tradedVolume") if self.__ex else None
        self.__traded_volume = traded_volume if traded_volume else []

    def __set_average_back_price(self):

        self.__tBPn = 0
        self.total_back_size = 0

        for trade in self.__traded_volume:
            self.__tBPn += trade.get("size") * trade.get("price")
            self.total_back_size += trade.get("size")

        self.average_back_price = self.__tBPn / self.total_back_size if self.total_back_size else nan

        return None

    def __set_average_lay_price(self):

        self.__tLPn = 0
        self.total_lay_size = 0

        for trade in self.__traded_volume:

            self.__tLPn += (
                trade.get("size")
                * (trade.get("price") - 1)
                * self.__calc_lay_odds(trade.get("price"))
            )
            self.total_lay_size += trade.get("size") * (trade.get("price") - 1)

        self.average_lay_price = self.__tLPn / self.total_lay_size if self.total_lay_size else nan
