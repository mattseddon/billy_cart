from tests.utils import GIVEN, WHEN, THEN
from tests.mock.mediator import MockMediator

from infrastructure.storage.historical.download.file.handler import (
    HistoricalDownloadFileHandler,
)

from pytest import mark
from unittest.mock import patch


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_handler(mock_notify):
    GIVEN("a file and a directory with the correct market type")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    mediator = MockMediator()
    handler.set_mediator(mediator)

    THEN(
        "the first of the eligible records has a process time within 5 minutes of the market start time"
    )

    market_data = handler.get_file_as_list()
    first_eligible = market_data[0]
    assert first_eligible.get("extract_time") >= -60 * 5

    THEN("the first eligible record does not have a closed indicator set to true")
    assert first_eligible.get("closed_indicator") is False

    THEN(
        "the last of the eligible records has a process time after the market start time"
    )
    last_eligible = market_data[-2]
    assert last_eligible.get("extract_time") > 0

    THEN("the last eligible record has a closed indicator set to false")
    assert last_eligible.get("closed_indicator") is False

    THEN("the last of the records has a process time after the market start time")
    last_record = market_data[-1]
    assert last_record.get("extract_time") > last_eligible.get("extract_time")

    THEN("the last eligible record has a closed indicator set to true")
    assert last_record.get("closed_indicator") is True

    THEN("the times in the list are unique")
    assert len(handler._data._existing_times) == len(set(handler._data._existing_times))

    THEN("the extract times in the eligible records are unique")
    extract_times = [record.get("extract_time") for record in market_data]
    assert len(extract_times) == len(set(extract_times))

    for index, record in enumerate(market_data):
        THEN("each of the extract times is within the expected range")
        extract_time = record.get("extract_time")
        assert -5 * 60 <= extract_time < 60 * 60
        THEN("the extract time is a single second after the previous extract time")
        if index > 0:
            assert extract_time == (market_data[index - 1].get("extract_time") + 1)
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
        if index > 0 and market_data[index - 1].get("closed_indicator") is True:
            assert record.get("closed_indicator") is True

    WHEN("we call get_outcome")
    result = handler.get_outcome()

    THEN("the result is as expected")
    assert result == 19795432


@patch("tests.mock.mediator.MockMediator.notify")
def test_incorrect_type(mock_notify):
    GIVEN("a file and in a directory which contains the incorrect market type")
    directory = "./dev"
    file = "1.156749791.bz2"

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    mediator = MockMediator()
    handler.set_mediator(mediator)

    THEN("it has loaded not loaded the file as an iterator")
    assert handler.get_file_as_list() == []

    WHEN("we call get_market")
    market = handler.get_market()

    THEN("no data is returned")
    assert market is None

    THEN("the mediator was not called")
    assert mock_notify.call_args is None


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_get_market(mock_notify):
    GIVEN("a file and a directory with the correct market type")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)
    mediator = MockMediator()
    handler.set_mediator(mediator)

    WHEN("we call get market for every record in the file")
    for record in handler.get_file_as_list():
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
    initial_market_list = [
        {
            "extract_time": -298,
            "stuff": {"A": "remains unchanged", "B": "also remains unchanged"},
        },
        {"extract_time": -10, "stuff": {"A": "now changed", "B": "also changed"}},
        {"extract_time": 300, "done": True},
    ]
    initial_market = iter(initial_market_list)

    WHEN("we gap fill the data")
    market = list(handler._gap_fill(initial_market))
    THEN("the returned market has the expected length")
    assert len(market) == (298 + 300 + 1)

    THEN("the records between -298 and -10 have the correct properties")
    expected_record = initial_market_list[0]
    for index, record in enumerate(market[0:288]):
        expected_record["extract_time"] = -298 + index
        assert record == expected_record

    THEN("the records between -10 and 300 have the correct properties")
    expected_record = initial_market_list[1]
    for index, record in enumerate(market[288:598]):
        expected_record["extract_time"] = -10 + index
        assert record == expected_record

    THEN("the final record has the correct properties")
    assert market[-1] == initial_market_list[2]


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
