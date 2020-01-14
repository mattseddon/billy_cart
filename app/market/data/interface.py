from app.interface import Interface
from infrastructure.built_in.adapter.abstract_base import abstract_method


class MarketDataRecordInterface(metaclass=Interface):
    @abstract_method
    def convert(self):
        pass


class DataContainerInterface(metaclass=Interface):
    @abstract_method
    def new(self):
        pass

    @abstract_method
    def add_rows(self):
        pass

    @abstract_method
    def get_row_count(self):
        pass

    @abstract_method
    def get_column_count(self):
        pass

    @abstract_method
    def get_column(self):
        pass

    @abstract_method
    def get_last_column_entry(self):
        pass

    @abstract_method
    def has_column(self):
        pass

    @abstract_method
    def get_column_group_values(self):
        pass

    @abstract_method
    def get_index(self):
        pass

    @abstract_method
    def set_index(self):
        pass

    @abstract_method
    def set_column_group_name(self):
        pass

