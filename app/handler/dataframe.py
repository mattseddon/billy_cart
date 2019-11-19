from app.handler.file import FileHandler
from app.handler.record import RecordHandler
from app.third_party_adapter.json_utils import make_dict
from app.third_party_adapter.date_time import DateTime
from pandas import DataFrame


class DataFrameHandler:
    def __init__(self, directory, file):
        self._raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
        self._odfet = []
        self._odfid = []
        self._odfspb = []
        self._odfspl = []
        self._odfobo = []
        self._odfolo = []
        self._odfapb = []
        self._odftsb = []
        self._odfapl = []
        self._odftsl = []
        self._odfsbt = []
        self._odfslt = []
        self._removed = []
        self.last_removed = -DateTime.seconds_in_a_day()
        self.__get_market_time()
        self._extract()

    def __get_market_time(self):
        first_record = self._raw_data[0]
        market_time = make_dict(first_record).get("marketStartTime")
        self.__market_time = DateTime(market_time).get_epoch()

    # __make_dataframe

    def _extract(self):

        self._make_lists()

        self.odf = DataFrame(
            {
                "extract_time": self._odfet,
                "id": self._odfid,
                "sp_back": self._odfspb,
                "sp_back_taken": self._odfsbt,
                "spLay": self._odfspl,
                "sp_lay_liability_taken": self._odfslt,
                "average_price_backed": self._odfapb,
                "total_size_backed": self._odftsb,
                "average_price_layed": self._odfapl,
                "total_size_layed": self._odftsl,
                "offered_back_odds": self._odfobo,
                "offered_lay_dds": self._odfolo,
            }
        )

        self.odf = self.odf[~(self.odf["id"].isin(self._removed))]
        print(self.odf)

    def _make_lists(self):
        for raw_record in self._raw_data:
            try:
                self.__append_to_lists(raw_record)
            except Exception:
                None

    def __append_to_lists(self, raw_record):
        data = make_dict(raw_record)
        extract_time = DateTime(data.get("et")).get_epoch()
        try:
            self.__time_difference = extract_time - self.__market_time
        except:
            return None

        market_info = data.get("marketInfo")[0]  # for testing purposes only
        runners = market_info.get("runners")

        for runner in runners:
            record = RecordHandler(runner)
            if record.is_valid():
                self.__append_record(record=record)
            elif record.id not in self._removed:
                self._removed.append(record.id)
                self.__update_last_removed(record=record)

    def __append_record(self, record):

        self._odfet.append(self.__time_difference)
        self._odfid.append(record.id)

        self._odfspb.append(record.sp_back)
        self._odfsbt.append(record.sp_back_taken)

        self._odfspl.append(record.sp_lay)
        self._odfslt.append(record.sp_lay_liability_taken)

        self._odfapb.append(record.tBP)
        self._odftsb.append(record.tBPd)

        self._odfapl.append(record.tLP)
        self._odftsl.append(record.tLPd)

        self._odfobo.append(record.offered_back_odds)
        self._odfolo.append(record.offered_lay_odds)

        return None

    def __update_last_removed(self, record):
        self.last_removed = max(
            self.last_removed, record.removal_date - self.__market_time
        )
        return None
