from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.built_in.adapter.copy_utils import make_copy
from infrastructure.third_party.adapter.numpy_utils import round_down


class HistoricalDownloadFileDataHandler:
    def __init__(self, items, market_start_time):
        self._items = {
            item.get("id"): {
                "ex": {"atb": {}, "trd": {}, "atl": {}},
                "sp": {
                    "spn": None,
                    "spb": {},
                    "spl": {},
                },
            }
            for item in items
        }
        self._market_start_time = DateTime(market_start_time).get_epoch()
        self._existing_times = []
        self._record = {}
        self._closed_indicator = False
        self.__market_definition_change = None

    def set_record(self, record):
        self._record = record

    def process(self, record):
        data = {}
        self.set_record(record)
        extract_time = self.__calc_extract_time()

        if extract_time >= -(60 * 5) and extract_time not in self._existing_times:
            # as this time has not been seen we have just ticked past the second
            # i.e this change happened after the required time
            # we want to return the correct state whilst the second ticked over
            # therefore return the existing information
            # and append (_add) the new data to the object
            self._existing_times.append(extract_time)
            data["extract_time"] = extract_time
            data["items"] = make_copy(self._items)
            data["closed_indicator"] = make_copy(self._closed_indicator)

        self._add_exchange_data()
        self._add_starting_price_data()

        self.__set_market_definition_change()
        self._add_removal_data()
        self.__set_closed_indictor()

        return data

    def __calc_extract_time(self):
        return round_down(self.__get_process_time() - self._market_start_time)

    def __get_process_time(self):
        return DateTime(self._record.get("pt")).get_epoch()

    def _add_exchange_data(self):
        self._add_available_to_back()
        self._add_available_to_lay()
        self._add_traded_volume()

    def _add_starting_price_data(self):
        self._add_sp_back_taken()
        self._add_sp_lay_taken()
        self._add_sp_near_price()

    def __set_market_definition_change(self):
        self.__market_definition_change = (
            self._record.get("mc")[0].get("marketDefinition") or {}
        )

    def _add_removal_data(self):
        for removal in self.__get_removed_items():
            self._items[removal.get("id")]["removal_date"] = removal.get("removalDate")

    def __set_closed_indictor(self):
        in_play = self.__market_definition_change.get("inPlay")
        if in_play is not None:
            self._closed_indicator = in_play

    def _add_available_to_back(self):
        return self.__add_attribute(attribute="atb", attribute_type="ex")

    def _add_available_to_lay(self):
        return self.__add_attribute(attribute="atl", attribute_type="ex")

    def _add_traded_volume(self):
        return self.__add_attribute(attribute="trd", attribute_type="ex")

    def _add_sp_back_taken(self):
        return self.__add_attribute(attribute="spb", attribute_type="sp")

    def _add_sp_lay_taken(self):
        return self.__add_attribute(attribute="spl", attribute_type="sp")

    def _add_sp_near_price(self):
        attribute = "spn"
        for item in self.__get_attributes(attribute=attribute):
            self._items[item.get("id")]["sp"][attribute] = item.get(attribute)

    def __add_attribute(self, attribute, attribute_type):
        for item in self.__get_attributes(attribute=attribute):
            for change in item.get(attribute):
                price = change[0]
                size = change[1]
                self._items[item.get("id")][attribute_type][attribute][price] = size

                if not size:
                    del self._items[item.get("id")][attribute_type][attribute][price]

    def __get_attributes(self, attribute):
        return list(
            filter(
                lambda item: item.get(attribute) and item.get("id"),
                self._get_item_changes(),
            )
        )

    def _get_item_changes(self):
        return self._record.get("mc")[0].get("rc")

    def __get_removed_items(self):
        return filter(
            lambda item: item.get("removalDate"),
            self.__get_item_definition_changes(),
        )

    def __get_item_definition_changes(self):
        return self.__market_definition_change.get("runners") or []
