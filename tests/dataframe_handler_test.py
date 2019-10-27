from tests.utils import GIVEN, WHEN, THEN
from app.handler.dataframe import DataHandler
from pandas import DataFrame
from pandas.testing import assert_series_equal

def test_create_df():
    GIVEN("the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    WHEN("we instantiate the data_handler class")
    data = DataHandler(directory=directory,file=file)
    THEN("the object contains a dataframe")
    assert type(data.odf) is DataFrame
    assert len(data.odf.columns) == 12
    print(data.odf)
    assert len(data.odf.index) > len(data._raw_data)
