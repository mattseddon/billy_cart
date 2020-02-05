from tests.utils import GIVEN, WHEN, THEN
from infrastructure.storage.historical.external_api.file.handler import (
    HistoricalExternalAPIFileHander,
)
from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.third_party.adapter.numpy_utils import round_down


def test_handler():
    GIVEN("a directory, an historical external api file and a handler")
    directory = "./data/29220705"
    file_name = "1.157190397.txt"
    file = HistoricalExternalAPIFileHander(directory=directory, file=file_name)

    WHEN("we get the file as a list")
    file_data = file.get_file_as_list()

    THEN("the data is a list")
    assert type(file_data) is list

    THEN(
        "the file has a record for every 5 seconds in the 4 minutes 27 seconds leading up to 33 seconds before the race"
    )
    assert len(file_data) == round_down(((5 * 60) - 33) / 5)

    for record in file_data:
        THEN("each record in the file data has a process time")
        assert type(record.get("process_time")) is str
        THEN("none of the records have marketInfo")
        assert record.get("marketInfo") is None

    WHEN("we get the market start time")
    market_start_time = file.get_market_start_time()

    THEN("the market_start_time is a string")
    assert type(market_start_time) is str

    THEN("the market start time can be converted to an epoch")
    epoch = DateTime(market_start_time).get_epoch()
    assert epoch > 0
