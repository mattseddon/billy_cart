from app.third_party_adapter.date_time import DateTime
from app.data.external_api.adapter.item import ItemAdapter
from pandas import DataFrame

class RecordAdapter:
    def convert(self, raw_record):
        self.__data = raw_record
        try:
            time_difference = self.__get_time_difference()
        except:
            return None

        items = self.__get_items()
        input_data = self.__process(items)
        df = DataFrame(input_data)
        df["extract_time"] = time_difference
        df.set_index(("extract_time", ""), inplace=True)
        df.columns.set_names(['variable','id'], inplace=True)
        return df

    def __get_time_difference(self):
        extract_time = DateTime(self.__data.get("et")).get_epoch()
        time_difference = (
            extract_time - DateTime(self.__data.get("marketStartTime")).get_epoch()
        )
        return time_difference

    def __get_items(self):
        market_info = self.__get_market_info()
        return market_info.get("runners")

    def __get_market_info(self):
        market_info = self.__data.get("marketInfo")
        return market_info[0] if type(market_info) is list else market_info

    def __process(self, items):
        data = {}
        for item in items:
            item_data = ItemAdapter(item)
            if item_data.is_valid():
                for column in [
                    "removal_date",
                    "sp_back",
                    "sp_back_taken",
                    "sp_lay",
                    "sp_lay_taken",
                    "average_price_backed",
                    "total_size_backed",
                    "average_price_layed",
                    "total_size_layed",
                    "offered_back_price",
                    "offered_lay_price",
                ]:
                    data[(column, item_data.get("id"))] = [item_data.get(column)]
        return data
