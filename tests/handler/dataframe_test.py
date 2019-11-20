from tests.utils import GIVEN, WHEN, THEN
from app.handler.dataframe import DataFrameHandler
from app.third_party_adapter.date_time import DateTime
from pandas import DataFrame

def test_create_df():
    GIVEN("the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    WHEN("we instantiate the data_handler class")
    data = DataFrameHandler(directory=directory,file=file)
    THEN("the object contains a dataframe")
    assert type(data.odf) is DataFrame
    THEN("the dataframe has the correct number of columns")
    assert len(data.odf.columns) == 12
    THEN("the dataframe has more records than the object's raw data")
    assert len(data.odf.index) > len(data._raw_data)

    GIVEN("the directory and file name of a test file which contains a removed runner")
    directory = "./data/29201704"
    file = "1.156695742.txt"
    WHEN("we instantiate the data_handler class")
    data = DataFrameHandler(directory=directory,file=file)
    removed_id = 23475685
    THEN("the object contains a dataframe")
    assert type(data.odf) is DataFrame
    THEN("the dataframe has the correct number of columns")
    assert len(data.odf.columns) == 12
    THEN("the dataframe has more records than the object's raw data")
    assert len(data.odf.index) > len(data._raw_data)