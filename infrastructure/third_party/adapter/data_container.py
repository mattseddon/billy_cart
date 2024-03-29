from pandas import DataFrame

from infrastructure.third_party.adapter.numpy_utils import make_native_type
from app.market.data.interface import DataContainerInterface


class DataContainer(DataContainerInterface):
    def __init__(self, data=None):
        if data:
            self.__frame = DataFrame(data)
        else:
            self.__frame = DataFrame()

    def new(self, data=None):
        return DataContainer(data)

    def add_rows(self, container):
        self.__frame = self.__frame.append(
            container._get_frame(), ignore_index=False, sort=True
        )

    def get_column_group_values(self, name):
        index = self.__frame.columns.unique(level=name)
        return index.tolist()

    def set_column_group_name(self, name=None, names=None, level=None):
        self.__frame.columns.set_names(name or names, level=level, inplace=True)

    def sum_columns(self, output, columns):
        self.__frame[output] = self.__frame[columns].fillna(0).sum(axis=1)

    def get_column(self, name):
        return self.__frame[name].tolist()

    def has_column(self, name):
        return name in self.__frame.columns.to_list()

    def get_row_count(self):
        return len(self.__frame.index)

    def get_column_count(self):
        return len(self.__frame.columns)

    def set_index(self, columns):
        self.__frame.set_index(columns, inplace=True)

    def get_last_column_entry(self, name):
        return make_native_type(self.__frame[name].iloc[-1])

    def get_index(self):
        return self.__frame.index.values.tolist()

    def _get_frame(self):
        return self.__frame
