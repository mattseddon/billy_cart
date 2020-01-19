from infrastructure.storage.file.handler import FileHandler
from infrastructure.storage.historical.download.file.data.handler import (
    HistoricalDownloadFileDataHandler,
)

from infrastructure.built_in.adapter.copy_utils import make_copy


class HistoricalDownloadFileHandler(FileHandler):
    def __init__(self, directory, file):
        super().__init__(directory=directory, file=file)
        self._file_data = super().get_file_as_list()
        self._market_definition = self._get_market_definition()
        self._data = HistoricalDownloadFileDataHandler(
            items=self._get_items_definition(),
            market_start_time=self.__get_market_start_time(),
        )
        market = list(
            filter(
                lambda record: record,
                map(lambda record: self._data.process(record), self._file_data),
            )
        )
        self._market = self._gap_fill(market=market)

    def __get_market_start_time(self):
        return self._market_definition.get("marketTime")

    def get_file_as_list(self):
        return self._market

    def _gap_fill(self, market):
        m = []
        for index, record in enumerate(market):
            if index > 0:
                previous_record = market[index - 1]
                m.extend(
                    self.__make_extra_records(
                        frm=previous_record,
                        time_diff=(
                            record.get("extract_time")
                            - (previous_record.get("extract_time"))
                        ),
                    )
                )
            m.append(record)
        return m

    def __make_extra_records(self, frm, time_diff):
        extra_records = []
        for seconds in range(1, time_diff):
            record = make_copy(frm)
            record["extract_time"] += seconds
            extra_records.append(record)
        return extra_records

    def _get_market_definition(self):
        return self._file_data[0].get("mc")[0].get("marketDefinition")

    def _get_items_definition(self):
        return self._market_definition.get("runners")

