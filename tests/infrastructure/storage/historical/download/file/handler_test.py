from tests.utils import GIVEN, WHEN, THEN
from tests.mock.mediator import MockMediator

from infrastructure.storage.historical.download.file.handler import (
    HistoricalDownloadFileHandler,
)
from infrastructure.built_in.adapter.date_time import DateTime

from pytest import mark
from unittest.mock import patch


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_handler(mock_notify):
    GIVEN("a file and a directory")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    mediator = MockMediator()
    handler.set_mediator(mediator)

    THEN("it has loaded the file as a list")
    assert type(handler._file_data) is list

    THEN("the list has hundreds of records")
    assert len(handler._file_data) > 200

    THEN("the list's first record has all of the items")
    first_record = handler._file_data[0]
    items = first_record.get("mc")[0].get("marketDefinition").get("runners")
    assert type(items) is list

    THEN("the list's first record has the market time")
    market_time = DateTime(
        first_record.get("mc")[0].get("marketDefinition").get("marketTime")
    ).get_epoch()
    assert market_time == 1569840120.0

    THEN("the first record has a process time which can be converted to an epoch")
    process_time = __get_process_time(first_record)
    assert type(process_time) is float

    THEN("the process time is within 24 hours of the market_time")
    assert (market_time - process_time) < (60 * 60 * 24)

    THEN("the handler's file data has a last record")
    last_record = handler._file_data[-1]

    THEN("the process time is after the market time but within 20 minutes")
    process_time = __get_process_time(last_record)
    assert (20 * 60) > -(market_time - process_time) > 0

    THEN("the handler has a list of eligible records")
    assert type(handler._market) is list

    THEN("the list of eligible records is non empty")
    assert len(handler._market) > 0

    THEN("the list of eligible records has less records than the original file")
    assert len(handler._market) < len(handler._file_data)

    THEN(
        "the first of the eligible records has a process time within 5 minutes of the market start time"
    )
    first_eligible = handler._market[0]
    assert first_eligible.get("extract_time") >= -60 * 5

    THEN("the first eligible record does not have a closed indicator set to true")
    assert first_eligible.get("closed_indicator") == False

    THEN(
        "the last of the eligible records has a process time after the market start time"
    )
    last_eligible = handler._market[-1]
    assert last_eligible.get("extract_time") > 0

    THEN("the last eligible record has a closed indicator set to true")
    assert last_eligible.get("closed_indicator") == True

    THEN(
        "the adapter has less entries than the handler's market (missing seconds filled)"
    )
    assert len(handler._market) >= len(handler._data._existing_times)

    THEN("the times in the list are unique")
    assert len(handler._data._existing_times) == len(set(handler._data._existing_times))

    THEN("the extract times in the eligible records are unique")
    extract_times = [record.get("extract_time") for record in handler._market]
    assert len(extract_times) == len(set(extract_times))

    for index, record in enumerate(handler._market):
        THEN("each of the extract times is within the expected range")
        extract_time = record.get("extract_time")
        assert -5 * 60 <= extract_time < 60 * 60
        THEN("the extract time is a single second after the previous extract time")
        if index > 0:
            assert extract_time == (handler._market[index - 1].get("extract_time") + 1)
        THEN("each of the eligible records has a dict of items")
        items = record.get("items")
        assert type(items) is dict
        THEN("the keys of the items dict matches the ids of the items")
        assert list(items.keys()) == __get_test_ids()
        THEN("each of the items has no 0 value for each attribute and a starting price")
        for id in __get_test_ids():
            assert items[id]["sp"]["spn"]
            assert 0 not in items[id]["ex"]["atb"].values()
            assert 0 not in items[id]["ex"]["atl"].values()
            assert 0 not in items[id]["ex"]["trd"].values()
            assert 0 not in items[id]["sp"]["spb"].values()
            assert 0 not in items[id]["sp"]["spl"].values()
        THEN("once the closed indicator becomes true is does not change back to false")
        if index > 0 and handler._market[index - 1].get("closed_indicator") == True:
            assert record.get("closed_indicator") == True

    WHEN("we call get market for every record in the file")
    for record in handler._market:
        handler.get_market()

        THEN("the correct data is sent to the mediator")
        args, kwargs = mock_notify.call_args
        assert args == ()
        data = kwargs.get("data")
        assert data == record


@patch(
    "infrastructure.storage.historical.download.file.handler.HistoricalDownloadFileHandler.__init__"
)
def test_gap_fill(mock_handler_init):
    GIVEN("a handler and some data")
    mock_handler_init.return_value = None
    handler = HistoricalDownloadFileHandler(file="weeeee", directory="waaaaaah")
    initial_market = [
        {
            "extract_time": -298,
            "stuff": {"A": "remains unchanged", "B": "also remains unchanged"},
        },
        {"extract_time": -10, "stuff": {"A": "now changed", "B": "also changed"}},
        {"extract_time": 300, "done": True},
    ]

    WHEN("we gap fill the data")
    market = handler._gap_fill(initial_market)

    THEN("the returned market has the expected length")
    assert len(market) == (298 + 300 + 1)

    THEN("the records between -298 and -10 have the correct properties")
    expected_record = initial_market[0]
    for index, record in enumerate(market[0:288]):
        expected_record["extract_time"] = -298 + index
        assert record == expected_record

    THEN("the records between -10 and 300 have the correct properties")
    expected_record = initial_market[1]
    for index, record in enumerate(market[288:598]):
        expected_record["extract_time"] = -10 + index
        assert record == expected_record

    THEN("the final record has the correct properties")
    assert market[-1] == initial_market[2]


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_post_order(mock_notify):
    GIVEN("a file, a directory and a mock mediator")
    directory = "./dev"
    file = "1.163093692.bz2"
    mediator = MockMediator()

    WHEN("we instantiate the handler and post a valid order")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    handler.set_mediator(mediator)
    id = 2121212
    orders = [{"id": id, "type": "BUY", "ex_price": 2.5, "size": 1000000}]
    handler.post_order(orders)

    THEN("the correct data is passed to the mediator")
    args, kwargs = mock_notify.call_args
    assert args == ()
    data = kwargs.get("data")
    assert data.get("response") == [
        {"instruction": {"selectionId": id}, "status": "SUCCESS"}
    ]
    assert data.get("orders") == orders


def test_get_result():
    GIVEN("a file and a directory")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler and and call get_result")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    result = handler.get_outcome()

    THEN("the result is as expected")
    assert result == 19795432


def __get_process_time(record):
    return DateTime(record.get("pt")).get_epoch()


def __get_test_ids():
    return [
        26291825,
        19795432,
        418,
        26291824,
        26291827,
        25197628,
        21145599,
        26291826,
    ]
