from app.data.external_api.adapter.record import RecordAdapter
from pandas import DataFrame


class DataHandler:
    def __init__(self):
        self.__odf = DataFrame()
        self.__adapter = RecordAdapter()

    def add(self, data):

        record_df = self.__adapter.convert(data)
        if record_df is not None:
            self.__odf = self.__odf.append(record_df, ignore_index=True)

        return None

    def _get_row_count(self):
        return len(self.__odf.index)

    def _get_column_count(self):
        return len(self.__odf.columns)

    def get_unique_ids(self):
        return self.__odf.columns.unique(level='id').values