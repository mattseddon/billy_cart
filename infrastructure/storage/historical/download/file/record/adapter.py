from app.market.data.utils import is_a_number
from app.market.data.interface import MarketDataRecordInterface

from infrastructure.third_party.adapter.numpy_utils import not_a_number


class HistoricalDownloadFileRecordAdapter(MarketDataRecordInterface):
    def convert(self, data):
        adapted_data = {}
        adapted_data["extract_time"] = data["extract_time"]
        adapted_data["closed_indicator"] = data["closed_indicator"]
        adapted_data["items"] = [
            self.__make_item(id, dict) for id, dict in data.get("items").items()
        ]
        return adapted_data

    def __make_item(self, id, dict):
        item = {
            "id": id,
            "sp_back_size": self.__calc_sp_back_size(dict),
            "ex_back_size": self.__calc_ex_back_size(dict),
            "sp_back_price": self.__get_sp_back_price(dict),
            "ex_average_back_price": self.__calc_ex_average_back_price(dict),
            "ex_offered_back_price": self.__get_ex_offered_back_price(dict),
            "sp_lay_size": self.__calc_sp_lay_size(dict),
            "ex_lay_size": self.__calc_ex_lay_size(dict),
            "sp_lay_price": self.__calc_sp_lay_price(dict),
            "ex_average_lay_price": self.__calc_ex_average_lay_price(dict),
            "ex_offered_lay_price": self.__get_ex_offered_lay_price(dict),
        }
        if dict.get("removal_date"):
            item["removal_date"] = dict.get("removal_date")
        return item

    def __calc_ex_back_size(self, dict):
        return self._sum_valid_sizes(dict.get("ex").get("trd"))

    def __calc_sp_back_size(self, dict):
        return self._sum_valid_sizes(dict.get("sp").get("spb"))

    def __calc_sp_lay_size(self, dict):
        return self._sum_valid_sizes(dict.get("sp").get("spl"))

    def __get_sp_back_price(self, dict):
        return dict.get("sp").get("spn")

    def __calc_ex_average_back_price(self, dict):
        valid_trades = self.__get_valid_entries(dict.get("ex").get("trd"))
        total_size = sum(valid_trades.values())
        return (
            sum([price * size for price, size in valid_trades.items()]) / total_size
            if total_size
            else not_a_number()
        )

    def __calc_ex_lay_size(self, dict):
        return sum(self.__calc_lay_liabilities(dict.get("ex").get("trd")))

    def __calc_lay_liabilities(self, dict):
        return [
            size * (price - 1) for price, size in self.__get_valid_entries(dict).items()
        ]

    def __calc_sp_lay_price(self, dict):
        sp_back_price = self.__get_sp_back_price(dict)
        return (
            self.__calc_sell_price(sp_back_price)
            if self.__is_valid(sp_back_price)
            else not_a_number()
        )

    def __calc_ex_average_lay_price(self, dict):
        trades = dict.get("ex").get("trd")
        valid_trades = self.__get_valid_entries(trades)
        liabilities = self.__calc_lay_liabilities(trades)
        total_liability = sum(liabilities)
        return (
            sum(
                self.__calc_sell_price(buy_price) * liability
                for buy_price, liability in zip(valid_trades.keys(), liabilities)
            )
            / total_liability
            if total_liability
            else not_a_number()
        )

    def __calc_sell_price(self, buy_price):
        return 1 / (1 - (1 / buy_price))

    def __get_ex_offered_back_price(self, dict):
        return self._get_max_valid_price(dict.get("ex").get("atb"))

    def __get_ex_offered_lay_price(self, dict):
        return self._get_min_valid_price(dict.get("ex").get("atl"))

    def _get_max_valid_price(self, dict):
        valid_prices = self.__get_valid_prices(dict)
        return max(valid_prices) if valid_prices else not_a_number()

    def _get_min_valid_price(self, dict):
        valid_prices = self.__get_valid_prices(dict)
        return min(valid_prices) if valid_prices else not_a_number()

    def __get_valid_prices(self, dict):
        return [price for price in dict.keys() if self.__is_valid(price)]

    def _sum_valid_sizes(self, dict):
        return sum(self.__get_valid_entries(dict).values())

    def __get_valid_entries(self, dict):
        return {
            price: size
            for price, size in dict.items()
            if self.__is_valid(price) and self.__is_valid(size)
        }

    def __is_valid(self, x):
        return is_a_number(x) and x > 0
