from app.handler.file import FileHandler
from app.runner_handler import RunnerHandler
from app.third_party_adapter.json_utils import make_dict
from app.third_party_adapter.date_time import DateTime
from pandas import DataFrame


class DataHandler:
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
        # lastRemoved required later in the process and are static but have had the wrong one
        # come through when two races run at the same time
        self.last_removed = -1000000
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
                "runnerId": self._odfid,
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

        self.odf = self.odf[~(self.odf["runnerId"].isin(self._removed))]
        print(self.odf)

    def _make_lists(self):
        # go through the list of dictionaries and pull out the required information
        # note this is done once for all tests - efficiency
        for raw_record in self._raw_data:
            try:
                self.__append_to_lists(raw_record)

            # when the data has been extracted every 5 seconds it is possible for 2 session to write into the same record.
            # This just makes sure that we miss that record
            except Exception:
                ##                print (e)
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
            rh = RunnerHandler(
                runner, removed=self._removed, market_time=self.__market_time
            )
            if rh.is_valid_runner():
                self.__append_runner(runner=rh)
            else:
                self._removed = rh.removed

    def __append_runner(self,runner):

        self._odfet.append(self.__time_difference)
        self._odfid.append(runner.id)

        self._odfspb.append(runner.sp_back)
        self._odfsbt.append(runner.sp_back_taken)

        self._odfspl.append(runner.sp_lay)
        self._odfslt.append(runner.sp_lay_liability_taken)

        self._odfapb.append(runner.tBP)
        self._odftsb.append(runner.tBPd)

        self._odfapl.append(runner.tLP)
        self._odftsl.append(runner.tLPd)

        self._odfobo.append(runner.offered_back_odds)
        self._odfolo.append(runner.offered_lay_odds)

        return None