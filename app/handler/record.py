from app.third_party_adapter.date_time import DateTime
from numpy import nan


class RecordHandler:
    def __init__(self, runner, removed, market_time):
        self.__runner = runner
        self.removed = removed
        self.__market_time = market_time
        self.id = self.__runner.get("selectionId")
        self.__status = self.__runner.get("status")
        self.__removal_date = self.__runner.get("removalDate")
        self.__sp = runner.get("sp")
        self.__ex = runner.get("ex")
        self.sp_back = self.__get_sp_back()
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
        if self.is_valid_runner():
            self.__append_runner_to_list()

    def is_valid_runner(self):
        self.__check_if_runner_removed()
        return (
            True if self.__runner_is_active() and self.__runner_has_price() else False
        )

    def __runner_is_active(self):
        return True if not (self.__has_been_removed()) else False

    def __check_if_runner_removed(self):
        # if there has been a horse removed last on then we will reset the market filter criteria (as it will change the odds)
        if self.__runner_removed():
            self.__remove_runner()
            self.__update_last_removed()

    def __runner_removed(self):
        return (
            True
            if (
                self.__status == "REMOVED"
                and self.__removal_date
                and not (self.__has_been_removed())
            )
            else False
        )

    def __runner_has_price(self):
        return True if self.__runner_has_valid_price(price=self.sp_back) else False

    def __runner_has_valid_price(self, price):
        return False if price in ["Infinity", "NaN", 0] else True

    def __has_been_removed(self):
        return True if (self.id in self.removed) else False

    def __remove_runner(self):
        self.removed.append(self.id)
        return None

    def __update_last_removed(self):
        self.last_removed = max(
            self.last_removed,
            DateTime(self.__removal_date).get_epoch() - self.__market_time,
        )
        return None

    def __append_runner_to_list(self):

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

    def __get_sp_back(self):
        if self.__sp:
            sp_back = self.__sp.get("nearPrice")
        else:
            sp_back = 0
        return sp_back

    def __calc_lay_odds(self, odds):
        """
        return the lay odds from the back odds
        """
        try:
            lay_odds = 1 / (1 - (1 / odds))
        except:
            lay_odds = nan

        return lay_odds
