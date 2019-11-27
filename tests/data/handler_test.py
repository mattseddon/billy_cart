from tests.utils import GIVEN, WHEN, THEN
from app.data.handler import DataHandler
from app.handler.file import FileHandler
from app.third_party_adapter.date_time import DateTime
from pandas import DataFrame


def test_create_df():
    GIVEN("the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)

    WHEN("we feed the data into a handler one record at a time")
    data = DataHandler()
    for i, raw_record in enumerate(raw_data):
        data.add(raw_record)
        number_records_processed = i + 1
        THEN("the dataframe the correct number of records")
        assert data._get_row_count() == number_records_processed

    WHEN("we have finished")
    THEN("the dataframe has the correct number of columns")
    assert data._get_column_count() == number_runners * __get_number_columns()
    THEN("the dataframe has the same number of records as the raw data")
    assert data._get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(data.get_unique_ids()) == number_runners


def test_removed_runner_df():
    GIVEN("the directory and file name of a test file which contains a removed runner")
    directory = "./data/29201704"
    file = "1.156695742.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)

    WHEN("we feed the data into a handler one record at a time")
    data = DataHandler()
    for i, raw_record in enumerate(raw_data):
        data.add(raw_record)
        number_records_processed = i + 1
        THEN("the dataframe the correct number of records")
        assert data._get_row_count() == number_records_processed

    WHEN("we have finished")
    THEN("the dataframe has the correct number of columns")
    assert data._get_column_count() == number_runners * __get_number_columns()
    THEN("the dataframe has the same number of records as the raw data")
    assert data._get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(data.get_unique_ids()) == number_runners


def __get_number_runners(data):
    return len(__get_runners(data))


def __get_runners(data):
    return data[0].get("marketInfo")[0].get("runners")


def __get_number_columns():
    return 11
