from app.third_party_adapter.date_time import DateTime
from numpy import nan


class RecordHandler:
    def __init__(self, record):
        self.id = record.get("selectionId")

        self.__status = record.get("status")
        self.__set_removal_date(record.get("removalDate"))

        self.__sp = record.get("sp")
        self.__ex = record.get("ex")
        self.__set_sp_back()
        self.__set_defaults()

        if self.is_valid():
            self.__extract_data()

    def __set_removal_date(self, removal_date):
        self.removal_date = DateTime(removal_date).get_epoch() if removal_date else None

    def __set_sp_back(self):
        if self.__sp:
            self.sp_back = self.__sp.get("nearPrice")
        else:
            self.sp_back = 0
        return None

    def __set_defaults(self):
        self.tBPn = 0
        self.tBPd = 0
        self.tBP = nan
        self.tLPn = 0
        self.tLPd = 0
        self.tLP = nan
        self.offered_back_odds = 0
        self.offered_lay_odds = 0
        self.sp_back_taken = 0
        self.sp_lay_liability_taken = 0
        return None

    def is_valid(self):
        return True if self.__is_active() and self.__has_price() else False

    def __is_active(self):
        return True if not (self.__removed()) else False

    def __removed(self):
        return True if (self.__status == "REMOVED" and self.removal_date) else False

    def __has_price(self):
        return True if self.__has_valid_price(price=self.sp_back) else False

    def __has_valid_price(self, price):
        return False if price in ["Infinity", "NaN", 0] else True

    def __extract_data(self):

        if self.__sp:
            for price in self.__sp.get("backStakeTaken"):
                self.sp_back_taken += price.get("size")
            for price in self.__sp.get("layLiabilityTaken"):
                self.sp_lay_liability_taken += price.get("size")

        self.sp_lay = self.__calc_lay_odds(self.sp_back)

        if self.__ex.get("availableToBack"):
            self.offered_back_odds = self.__ex.get("availableToBack")[0].get("price")

        if self.__ex.get("availableToLay"):
            self.offered_lay_odds = self.__ex.get("availableToLay")[0].get("price")

        if self.__ex:
            traded_volume = self.__ex.get("tradedVolume")
            if traded_volume:
                for trade in traded_volume:
                    self.tBPn += trade.get("size") * trade.get("price")
                    self.tBPd += trade.get("size")

                    self.tLPn += (
                        trade.get("size")
                        * (trade.get("price") - 1)
                        * self.__calc_lay_odds(trade.get("price"))
                    )
                    self.tLPd += trade.get("size") * (trade.get("price") - 1)

                if self.tBPd:
                    self.tBP = self.tBPn / self.tBPd

                if self.tLPd:
                    self.tLP = self.tLPn / self.tLPd

    def __calc_lay_odds(self, odds):
        """
        return the lay odds from the back odds
        """
        try:
            lay_odds = 1 / (1 - (1 / odds))
        except:
            lay_odds = nan

        return lay_odds
