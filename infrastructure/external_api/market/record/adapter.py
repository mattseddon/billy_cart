from app.market.data.interface import ExternalAPIMarketDataInterface
from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.external_api.market.record.item.adapter import ItemAdapter


class RecordAdapter(ExternalAPIMarketDataInterface):
    def convert(self, raw_record):
        self.__data = raw_record

        items = self.__get_items()
        if not (items):
            return None

        try:
            time_difference = self.__get_time_difference()
        except:
            return None

        data = self.__process(items)
        if data.get("items"):
            data["extract_time"] = time_difference
            data["closed_indicator"] = self.__get_closed_indicator()
            return data
        else:
            return None

    def __get_time_difference(self):
        extract_time = DateTime(self.__data.get("et")).get_epoch()
        time_difference = (
            extract_time - DateTime(self.__data.get("marketStartTime")).get_epoch()
        )
        return time_difference

    def __get_items(self):
        market_info = self.__get_market_info()
        return market_info.get("runners") if market_info else None

    def __process(self, items):
        data = {}
        data["items"] = self.__non_empty(
            map(lambda item: ItemAdapter(item).get_adapted_data(), items)
        )
        return data

    def __get_market_info(self):
        market_info = self.__data.get("marketInfo")
        return market_info[0] if type(market_info) is list else market_info

    def __non_empty(self, items):
        return list(filter(None, items))

    def __get_closed_indicator(self):
        return self.__get_market_info().get("inplay")
