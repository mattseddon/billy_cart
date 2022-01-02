from app.market.data.interface import MarketDataRecordInterface
from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.external_api.market.record.item.adapter import ItemAdapter


class ExternalAPIMarketRecordAdapter(MarketDataRecordInterface):
    def __init__(self, market_start_time):
        self.__market_start_time = DateTime(market_start_time).get_epoch()
        self.__data = None

    def convert(self, raw_record):
        self.__data = raw_record

        items = self.__get_items()
        if not items:
            return None

        try:
            time_difference = self._get_time_difference()
        except:
            return None

        data = self.__process(items)
        if data.get("items"):
            data["extract_time"] = time_difference
            data["closed_indicator"] = self.__get_closed_indicator()
            return data

        return None

    def _get_time_difference(self):
        extract_time = DateTime(self.__data.get("process_time")).get_epoch()
        return extract_time - self.__market_start_time

    def __get_items(self):
        return self.__data.get("runners")

    def __process(self, items):
        data = {}
        data["items"] = self.__non_empty(
            map(lambda item: ItemAdapter(item).get_adapted_data(), items)
        )
        return data

    def __non_empty(self, items):
        return list(filter(None, items))

    def __get_closed_indicator(self):
        return self.__data.get("inplay")
