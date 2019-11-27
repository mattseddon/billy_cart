from app.data.external_api.adapter.record import RecordAdapter
from pandas import DataFrame


class DataHandler:
    def __init__(self):
        self.odf = DataFrame()
        self.__adapter = RecordAdapter()

    def add(self, data):

        record_df = self.__adapter.convert(data)
        if record_df is not None:
            self.odf = self.odf.append(record_df, ignore_index=True)

        return None