from app.handler.file import FileHandler
from app.handler.record import RecordHandler
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
        self._odfrmd = []
        self.__get_market_time()
        self._extract()
        self._transform()

    def __get_market_time(self):
        first_record = self._raw_data[0]
        market_time = first_record.get("marketStartTime")
        self.__market_time = DateTime(market_time).get_epoch()

    def _extract(self):

        self._make_lists()

        self.odf = DataFrame(
            {
                "extract_time": self._odfet,
                "id": self._odfid,
                "removal_date": self._odfrmd,
                "sp_back": self._odfspb,
                "sp_back_taken": self._odfsbt,
                "sp_lay": self._odfspl,
                "sp_lay_taken": self._odfslt,
                "average_price_backed": self._odfapb,
                "total_size_backed": self._odftsb,
                "average_price_layed": self._odfapl,
                "total_size_layed": self._odftsl,
                "offered_back_price": self._odfobo,
                "offered_lay_price": self._odfolo,
            }
        )
        return None

    def _transform(self):

        self.odf["total_sp_backed"] = (
            self.odf["total_size_backed"] + self.odf["sp_back_taken"]
        )
        self.odf["total_sp_layed"] = self.odf["total_size_layed"] + (
            self.odf["sp_lay_taken"] * (self.odf["sp_back"] - 1)
        )

        odf = self.odf.sort_values(by=["extract_time", "id"]).drop_duplicates(
            ["extract_time", "id"], keep="last"
        )

        self.odfT = odf.pivot(
            index="extract_time",
            columns="id",
            values=[
                "removal_date",
                "sp_back",
                "total_sp_backed",
                "sp_lay",
                "total_sp_layed",
                "average_price_backed",
                "total_size_backed",
                "average_price_layed",
                "total_size_layed",
                "offered_back_price",
                "offered_lay_price",
            ],
        ).fillna(method="ffill")
        return None

    def _make_lists(self):
        for raw_record in self._raw_data:
            # try:
                self.__append_to_lists(raw_record)
            # except Exception:
                # return None

    def __append_to_lists(self, raw_record):
        try:
            data = raw_record
            extract_time = DateTime(data.get("et")).get_epoch()
            self.__time_difference = extract_time - self.__market_time
        except:
            return print(raw_record)

        market_info = data.get("marketInfo")[0]  # for testing purposes only
        runners = market_info.get("runners")

        for runner in runners:
            record = RecordHandler(runner)
            if record.is_valid():
                self.__append_record(record=record)

        return None

    def __append_record(self, record):

        self._odfet.append(self.__time_difference)
        self._odfid.append(record.id)

        self._odfspb.append(record.sp_back)
        self._odfsbt.append(record.sp_back_taken)

        self._odfspl.append(record.sp_lay)
        self._odfslt.append(record.sp_lay_taken)

        self._odfapb.append(record.average_back_price)
        self._odftsb.append(record.total_back_size)

        self._odfapl.append(record.average_lay_price)
        self._odftsl.append(record.total_lay_size)

        self._odfobo.append(record.offered_back_price)
        self._odfolo.append(record.offered_lay_price)

        self._odfrmd.append(record.removal_date)

        return None
