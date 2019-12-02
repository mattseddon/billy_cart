from app.third_party_adapter.date_time import DateTime
from app.data.external_api.adapter.item import ItemAdapter


class RecordAdapter:
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

    def __get_market_info(self):
        market_info = self.__data.get("marketInfo")
        return market_info[0] if type(market_info) is list else market_info

    def __process(self, items):
        data = {"items": []}
        for item in items:
            item_data = ItemAdapter(item)
            if item_data.is_valid():
                data["items"].append(item_data)
        return data
