from tests.utils import GIVEN, WHEN, THEN, almost_equal
from tests.mock.mediator import MockMediator

from app.market.data.handler import DataHandler
from app.market.metadata.handler import MetadataHandler
from app.market.data.transform.price.handler import PriceHandler

from infrastructure.third_party.adapter.data_container import DataContainer
from infrastructure.third_party.adapter.numpy_utils import round_down
from infrastructure.storage.handler import FileHandler
from infrastructure.external_api.market.record.adapter import RecordAdapter


from pytest import mark
from unittest.mock import patch


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_handler(mock_notify):
    GIVEN("a data handler and the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    adapter = RecordAdapter()
    pricer = PriceHandler()
    metadata = MetadataHandler()
    mediator = MockMediator()

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(mediator=mediator, adapter=adapter, container=DataContainer())
    for i, raw_record in enumerate(raw_data):
        handler.process_data(raw_record)
        THEN("the incoming record was processed")
        number_records_processed = i + 1
        THEN("the handler's data has the correct number of records")
        assert handler._container.get_row_count() == number_records_processed
        assert (
            handler._container.get_last_column_entry(name=("closed_indicator", ""))
            == False
        )
        THEN("the mediator's notify method was called with the correct parameters")
        model_data = handler._get_model_data()
        args, kwargs = mock_notify.call_args
        assert args == ()
        assert kwargs.get("data") == model_data
        assert kwargs.get("event") == "data added to container"

        THEN("there is a record in the model data for each of the runners")
        assert len(model_data) == number_runners

        test_record = {
            each.get("id"): each for each in adapter.convert(raw_record).get("items")
        }
        total_sp_probability = 0
        total_ex_probability = 0

        for data in model_data:
            THEN("each of the items in the model data has an non-zero id")
            id = data.get("id")
            assert type(id) is int
            assert id > 0

            test_item = test_record.get(id)

            THEN("the data has the correct combined_back_size")
            combined_back_size = data.get(
                "combined_back_size" + metadata.get_point_in_time_suffix()
            )
            combined_back_size == (
                test_item.get("sp_back_size") + test_item.get("ex_back_size")
            )

            THEN(
                "the data contains the compositional sp probability which is between 0 and 1"
            )
            compositional_sp_probability = data.get(
                "compositional_sp_probability" + metadata.get_point_in_time_suffix()
            )
            total_sp_probability += compositional_sp_probability
            assert 1 > compositional_sp_probability > 0

            THEN(
                "the data contains the compositional ex probability which is between 0 and 1"
            )
            compositional_ex_average_probability = data.get(
                "compositional_ex_average_probability"
                + metadata.get_point_in_time_suffix()
            )
            total_ex_probability += compositional_ex_average_probability
            assert 1 > compositional_ex_average_probability > 0

            THEN("the data contains the correct offered price")
            offered_price = data.get(
                "ex_offered_back_price" + metadata.get_point_in_time_suffix()
            )
            assert offered_price > 0
            assert offered_price == test_item.get("ex_offered_back_price")

            THEN("the data contains the correct returns price")
            returns_price = data.get(
                "ex_offered_back_price_mc" + metadata.get_point_in_time_suffix()
            )
            assert returns_price > 0
            assert returns_price == pricer.remove_commission(
                test_item.get("ex_offered_back_price")
            )

            THEN("the sp back price time series data returned is of the correct length")
            compositional_sp_back_price_ts = data.get(
                "compositional_sp_back_price" + metadata.get_time_series_suffix()
            )
            assert len(compositional_sp_back_price_ts) == number_records_processed
            THEN("the last record of the time series data matches the probability")
            assert almost_equal(
                compositional_sp_back_price_ts[-1], 1 / compositional_sp_probability
            )

            THEN("the extract time time series data returned is of the correct length")
            extract_time_ts = data.get(
                "extract_time" + metadata.get_time_series_suffix()
            )
            assert len(extract_time_ts) == number_records_processed
            for i, extract_time in enumerate(extract_time_ts):
                if i > 0:
                    THEN("the times in the series are ascending")
                    assert extract_time > extract_time_ts[i - 1]

            THEN(
                "the combined back size time series data returned is of the correct length"
            )
            combined_back_size_ts = data.get(
                "combined_back_size" + metadata.get_time_series_suffix()
            )
            assert len(combined_back_size_ts) == number_records_processed
            THEN(
                "the last entry in the time series is the same as point in time combined_back_size"
            )
            assert combined_back_size_ts[-1] == combined_back_size
            for i, combined_back_size in enumerate(combined_back_size_ts):
                if i > 0:
                    THEN("the sizes in the series are ascending")
                    assert combined_back_size >= combined_back_size_ts[i - 1]

        THEN("the total ex and sp probabilities from the model_data sum to 1")
        assert almost_equal(total_sp_probability, 1)
        assert almost_equal(total_ex_probability, 1)

    WHEN("we have finished")
    THEN("the data container has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the data container has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_more_data(mock_notify):
    GIVEN("a data handler and the directory and file name of a test file")

    directory = "./data/29451865"
    file = "1.162069495.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    adapter = RecordAdapter()
    pricer = PriceHandler()
    metadata = MetadataHandler()
    mediator = MockMediator()

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(
        mediator=mediator, adapter=RecordAdapter(), container=DataContainer()
    )
    for i, raw_record in enumerate(raw_data):
        handler.process_data(raw_record)
        THEN("the incoming record was processed")

        number_records_processed = i + 1
        THEN("the handler's data has the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

        THEN("the mediator's notify method was called with the correct parameters")
        model_data = handler._get_model_data()
        args, kwargs = mock_notify.call_args
        assert args == ()
        assert kwargs.get("data") == model_data
        assert kwargs.get("event") == "data added to container"

        THEN("there is a record in the model data for each of the runners")
        assert len(model_data) == number_runners

        test_record = {
            each.get("id"): each for each in adapter.convert(raw_record).get("items")
        }
        total_sp_probability = 0
        total_ex_probability = 0

        for data in model_data:
            THEN("each of the items in the model data has an non-zero id")
            id = data.get("id")
            assert type(id) is int
            assert id > 0

            test_item = test_record.get(id)

            THEN("the data has the correct combined_back_size")
            combined_back_size = data.get(
                "combined_back_size" + metadata.get_point_in_time_suffix()
            )
            combined_back_size == (
                test_item.get("sp_back_size") + test_item.get("ex_back_size")
            )

            THEN(
                "the data contains the compositional sp probability which is between 0 and 1"
            )
            compositional_sp_probability = data.get(
                "compositional_sp_probability" + metadata.get_point_in_time_suffix()
            )
            total_sp_probability += compositional_sp_probability
            assert 1 > compositional_sp_probability > 0

            THEN(
                "the data contains the compositional ex probability which is between 0 and 1"
            )
            compositional_ex_average_probability = data.get(
                "compositional_ex_average_probability"
                + metadata.get_point_in_time_suffix()
            )
            total_ex_probability += compositional_ex_average_probability
            assert 1 > compositional_ex_average_probability > 0

            THEN("the data contains the correct offered price")
            offered_price = data.get(
                "ex_offered_back_price" + metadata.get_point_in_time_suffix()
            )
            assert offered_price > 0
            assert offered_price == test_item.get("ex_offered_back_price")

            THEN("the data contains the correct returns price")
            returns_price = data.get(
                "ex_offered_back_price_mc" + metadata.get_point_in_time_suffix()
            )
            assert returns_price > 0
            assert returns_price == pricer.remove_commission(
                test_item.get("ex_offered_back_price")
            )

            THEN("the sp back price time series data returned is of the correct length")
            compositional_sp_back_price_ts = data.get(
                "compositional_sp_back_price" + metadata.get_time_series_suffix()
            )
            assert len(compositional_sp_back_price_ts) == number_records_processed
            THEN("the last record of the time series data matches the probability")
            assert almost_equal(
                compositional_sp_back_price_ts[-1], 1 / compositional_sp_probability
            )

            THEN("the extract time time series data returned is of the correct length")
            extract_time_ts = data.get(
                "extract_time" + metadata.get_time_series_suffix()
            )
            assert len(extract_time_ts) == number_records_processed
            for i, extract_time in enumerate(extract_time_ts):
                if i > 0:
                    THEN("the times in the series are ascending")
                    assert extract_time > extract_time_ts[i - 1]

            THEN(
                "the combined back size time series data returned is of the correct length"
            )
            combined_back_size_ts = data.get(
                "combined_back_size" + metadata.get_time_series_suffix()
            )
            assert len(combined_back_size_ts) == number_records_processed
            THEN(
                "the last entry in the time series is the same as point in time combined_back_size"
            )
            assert combined_back_size_ts[-1] == combined_back_size
            for i, combined_back_size in enumerate(combined_back_size_ts):
                if i > 0:
                    THEN("the sizes in the series are ascending")
                    assert combined_back_size >= combined_back_size_ts[i - 1]

        THEN("the total ex and sp probabilities from the model_data sum to 1")
        assert almost_equal(total_sp_probability, 1)
        assert almost_equal(total_ex_probability, 1)

    WHEN("we have finished")
    THEN("the data container has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the data container has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


@mark.slow
@patch("tests.mock.mediator.MockMediator.notify")
def test_fixed_probability(mock_notify):
    GIVEN("a data handler and the directory and file name of a test file")

    directory = "./data/29451865"
    file = "1.162069495.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    unfixed_items = number_runners
    fixed_items = 0
    adapter = RecordAdapter()
    pricer = PriceHandler()
    metadata = MetadataHandler()
    mediator = MockMediator()
    correct_probability = 1

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(
        mediator=mediator, adapter=RecordAdapter(), container=DataContainer()
    )
    for i, raw_record in enumerate(raw_data):
        number_records_processed = i + 1
        if number_records_processed % 10 == 0:
            WHEN("we randomly fix the probability of an item")
            id_to_fix = handler._get_ids_for_model_data()[0]
            fixed_probability = round(
                handler._container.get_last_column_entry(
                    name=("compositional_sp_probability", id_to_fix)
                ),
                4,
            )
            handler._set_probability(id=id_to_fix, probability=fixed_probability)
            correct_probability -= fixed_probability
            unfixed_items -= 1
            fixed_items += 1

        fixed_probability_ids = handler._get_fixed_probability_ids()
        THEN("the list of fixed probability ids is the correct length")
        assert len(fixed_probability_ids) == fixed_items

        handler.process_data(raw_record)

        THEN("the handler's data has the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

        THEN("the mediator's notify method was called with the correct parameters")
        model_data = handler._get_model_data()
        args, kwargs = mock_notify.call_args
        assert args == ()
        assert kwargs.get("data") == model_data
        assert kwargs.get("event") == "data added to container"

        THEN("there is a record in the model data for each of the unfixed items")
        assert len(model_data) == unfixed_items

        test_record = {
            each.get("id"): each for each in adapter.convert(raw_record).get("items")
        }
        total_sp_probability = 0
        total_ex_probability = 0

        for data in model_data:
            THEN("each of the items in the model data has an non-zero id")
            id = data.get("id")
            assert type(id) is int
            assert id > 0

            THEN("the items probability has not been fixed")
            assert id not in fixed_probability_ids

            test_item = test_record.get(id)

            THEN("the data has the correct combined_back_size")
            combined_back_size = data.get(
                "combined_back_size" + metadata.get_point_in_time_suffix()
            )
            combined_back_size == (
                test_item.get("sp_back_size") + test_item.get("ex_back_size")
            )

            THEN(
                "the data contains the compositional sp probability which is between 0 and 1"
            )
            compositional_sp_probability = data.get(
                "compositional_sp_probability" + metadata.get_point_in_time_suffix()
            )
            total_sp_probability += compositional_sp_probability
            assert 1 > compositional_sp_probability > 0

            THEN(
                "the data contains the compositional ex probability which is between 0 and 1"
            )
            compositional_ex_average_probability = data.get(
                "compositional_ex_average_probability"
                + metadata.get_point_in_time_suffix()
            )
            total_ex_probability += compositional_ex_average_probability
            assert 1 > compositional_ex_average_probability > 0

            THEN("the data contains the correct offered price")
            offered_price = data.get(
                "ex_offered_back_price" + metadata.get_point_in_time_suffix()
            )
            assert offered_price > 0
            assert offered_price == test_item.get("ex_offered_back_price")

            THEN("the data contains the correct returns price")
            returns_price = data.get(
                "ex_offered_back_price_mc" + metadata.get_point_in_time_suffix()
            )
            assert returns_price > 0
            assert returns_price == pricer.remove_commission(
                test_item.get("ex_offered_back_price")
            )

            THEN("the sp back price time series data returned is of the correct length")
            compositional_sp_back_price_ts = data.get(
                "compositional_sp_back_price" + metadata.get_time_series_suffix()
            )
            assert len(compositional_sp_back_price_ts) == number_records_processed
            THEN("the last record of the time series data matches the probability")
            assert almost_equal(
                compositional_sp_back_price_ts[-1], 1 / compositional_sp_probability
            )

            THEN("the extract time time series data returned is of the correct length")
            extract_time_ts = data.get(
                "extract_time" + metadata.get_time_series_suffix()
            )
            assert len(extract_time_ts) == number_records_processed
            for i, extract_time in enumerate(extract_time_ts):
                if i > 0:
                    THEN("the times in the series are ascending")
                    assert extract_time > extract_time_ts[i - 1]

            THEN(
                "the combined back size time series data returned is of the correct length"
            )
            combined_back_size_ts = data.get(
                "combined_back_size" + metadata.get_time_series_suffix()
            )
            assert len(combined_back_size_ts) == number_records_processed
            THEN(
                "the last entry in the time series is the same as point in time combined_back_size"
            )
            assert combined_back_size_ts[-1] == combined_back_size
            for i, combined_back_size in enumerate(combined_back_size_ts):
                if i > 0:
                    THEN("the sizes in the series are ascending")
                    assert combined_back_size >= combined_back_size_ts[i - 1]

        THEN("the total ex and sp probabilities from the model_data sum to 1")
        assert almost_equal(total_sp_probability, correct_probability)
        assert almost_equal(total_ex_probability, correct_probability)

    WHEN("we have finished")
    THEN("the data container has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the data container has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners
    THEN("the correct number of fixed probabilities are contained in the object")
    assert len(handler._get_fixed_probability_ids()) == round_down(
        number_records_processed / 10
    )


@mark.slow
def test_removed_runner():
    GIVEN("the directory and file name of a test file which contains a removed runner")
    directory = "./data/29201704"
    file = "1.156695742.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    mediator = MockMediator()

    WHEN("we feed the data into a handler one record at a time")

    handler = DataHandler(
        mediator=mediator, adapter=RecordAdapter(), container=DataContainer()
    )
    for i, raw_record in enumerate(raw_data):
        handler.process_data(raw_record)
        THEN("the incoming record was processed")
        number_records_processed = i + 1
        THEN("the data container the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

    WHEN("we have finished")
    THEN("the data container has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the data container has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


def test_confirm_market_closed():
    GIVEN("a data handler and the directory and file name of a test file")
    adapter = RecordAdapter()
    mediator = MockMediator()

    handler = DataHandler(mediator=mediator, adapter=adapter, container=DataContainer())

    WHEN("we check if the market is closed")
    closed = handler._confirm_market_closed()
    THEN("it is not")
    assert not closed

    GIVEN(
        "the handler's container has the required column but it does not indicate that the market is closed"
    )
    closed_record = handler._container.new(data={("closed_indicator", ""): [0]})
    handler._container.add_rows(container=closed_record)

    WHEN("we check if the market is closed")
    closed = handler._confirm_market_closed()
    THEN("it is not")
    assert not closed

    GIVEN(
        "the handler's container has the required column indicating that the market is closed"
    )
    closed_record = handler._container.new(data={("closed_indicator", ""): [1]})
    handler._container.add_rows(container=closed_record)

    WHEN("we check if the market is closed")
    closed = handler._confirm_market_closed()
    THEN("it is")
    assert closed


def test_get_ids_for_model_data():
    GIVEN("a data handler with some data and two fixed probabilities")
    GIVEN("a data handler and the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    raw_record = FileHandler(directory=directory, file=file).get_file_as_list()[0]
    adapter = RecordAdapter()
    mediator = MockMediator()

    handler = DataHandler(mediator=mediator, adapter=adapter, container=DataContainer())
    handler.process_data(raw_record)

    WHEN(
        "we set the probabilities of two items and get the ids required for the next model run"
    )
    ids = handler.get_unique_ids()
    for id in ids[0:2]:
        handler._set_probability(id=id, probability=0.1)
        ids.pop(0)

    THEN("the list omits the items which have fixed probabilities")
    model_ids = handler._get_ids_for_model_data()
    assert model_ids == ids
    assert len(model_ids) < len(handler.get_unique_ids())


def __get_number_runners(data):
    return len(__get_runners(data))


def __get_runners(data):
    return data[0].get("marketInfo")[0].get("runners")


def __get_number_columns(number_runners):
    return (
        __get_number_columns_per_runner() * number_runners
    ) + __get_number_overarching_columns()


def __get_number_columns_per_runner():
    metadata_handler = MetadataHandler()
    number_default_columns = len(metadata_handler.get_required_variables())
    number_compositional_columns = 4
    number_size_columns = 1
    number_commission_adj_columns = len(metadata_handler.get_back_prices())
    return (
        number_default_columns
        + number_compositional_columns
        + number_size_columns
        + number_commission_adj_columns
    )


def __get_number_overarching_columns():
    number_index_columns = 1
    number_indicator_columns = 1
    return number_index_columns + number_indicator_columns

