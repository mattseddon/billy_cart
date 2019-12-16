from tests.utils import GIVEN, WHEN, THEN, almost_equal
from app.market.data.handler import DataHandler
from infrastructure.third_party.adapter.data_container import DataContainer
from infrastructure.storage.handler import FileHandler
from infrastructure.external_api.market.adapter.record import RecordAdapter


def test_handler():
    GIVEN("the directory and file name of a test file")
    directory = "./data/29184567"
    file = "1.156230797.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    adapter = RecordAdapter()

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(adapter=FakeAdapter(), container=DataContainer())
    for i, raw_record in enumerate(raw_data):
        adapted_data = adapter.convert(raw_record)
        handler.add(adapted_data)
        number_records_processed = i + 1
        THEN("the handler's data has the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

        WHEN("we get the model data")
        model_data = handler.get_model_data()
        THEN("there is a record for each of the runners")
        assert len(model_data) == number_runners

        test_record = {each.get("id"): each for each in adapted_data.get("items")}
        total_sp_probability = 0
        total_ex_probability = 0

        for data in model_data:
            THEN("each of the items in the model data has an non-zero id")
            id = data.get("id")
            assert type(id) is int
            assert id > 0

            test_item = test_record.get(id)

            THEN("the data has the correct combined_back_size")
            combined_back_size = data.get("combined_back_size")
            combined_back_size == (
                test_item.get("sp_back_size") + test_item.get("ex_back_size")
            )

            THEN(
                "the data contains the compositional sp probability which is between 0 and 1"
            )
            compositional_sp_probability = data.get("compositional_sp_probability")
            total_sp_probability += compositional_sp_probability
            assert 1 > compositional_sp_probability > 0

            THEN(
                "the data contains the compositional ex probability which is between 0 and 1"
            )
            compositional_ex_probability = data.get("compositional_ex_probability")
            total_ex_probability += compositional_ex_probability
            assert 1 > compositional_ex_probability > 0

            THEN("the data contains the correct offered price")
            offered_price = data.get("ex_offered_back_price")
            assert offered_price > 0
            assert offered_price == test_item.get("ex_offered_back_price")

            THEN("the sp back price time series data returned is of the correct length")
            compositional_sp_back_price_ts = data.get("compositional_sp_back_price_ts")
            assert len(compositional_sp_back_price_ts) == number_records_processed
            THEN("the last record of the time series data matches the probability")
            assert almost_equal(
                compositional_sp_back_price_ts[-1], 1 / compositional_sp_probability
            )

            THEN("the extract time time series data returned is of the correct length")
            extract_time_ts = data.get("extract_time_ts")
            assert len(extract_time_ts) == number_records_processed
            for i, extract_time in enumerate(extract_time_ts):
                if i > 0:
                    THEN("the times in the series are ascending")
                    assert extract_time > extract_time_ts[i - 1]

            THEN(
                "the combined back size time series data returned is of the correct length"
            )
            combined_back_size_ts = data.get("combined_back_size_ts")
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
    THEN("the dataframe has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the dataframe has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


def test_more_data():
    GIVEN("the directory and file name of a test file")
    directory = "./data/29451865"
    file = "1.162069495.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)
    adapter = RecordAdapter()

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(adapter=FakeAdapter(), container=DataContainer())
    for i, raw_record in enumerate(raw_data):
        adapted_data = adapter.convert(raw_record)
        handler.add(adapted_data)
        number_records_processed = i + 1
        THEN("the handler's data has the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

        WHEN("we get the model data")
        model_data = handler.get_model_data()
        THEN("there is a record for each of the runners")
        assert len(model_data) == number_runners

        test_record = {each.get("id"): each for each in adapted_data.get("items")}
        total_sp_probability = 0
        total_ex_probability = 0

        for data in model_data:
            THEN("each of the items in the model data has an non-zero id")
            id = data.get("id")
            assert type(id) is int
            assert id > 0

            test_item = test_record.get(id)

            THEN("the data has the correct combined_back_size")
            combined_back_size = data.get("combined_back_size")
            combined_back_size == (
                test_item.get("sp_back_size") + test_item.get("ex_back_size")
            )

            THEN(
                "the data contains the compositional sp probability which is between 0 and 1"
            )
            compositional_sp_probability = data.get("compositional_sp_probability")
            total_sp_probability += compositional_sp_probability
            assert 1 > compositional_sp_probability > 0

            THEN(
                "the data contains the compositional ex probability which is between 0 and 1"
            )
            compositional_ex_probability = data.get("compositional_ex_probability")
            total_ex_probability += compositional_ex_probability
            assert 1 > compositional_ex_probability > 0

            THEN("the data contains the correct offered price")
            offered_price = data.get("ex_offered_back_price")
            assert offered_price > 0
            assert offered_price == test_item.get("ex_offered_back_price")

            THEN("the sp back price time series data returned is of the correct length")
            compositional_sp_back_price_ts = data.get("compositional_sp_back_price_ts")
            assert len(compositional_sp_back_price_ts) == number_records_processed
            THEN("the last record of the time series data matches the probability")
            assert almost_equal(
                compositional_sp_back_price_ts[-1], 1 / compositional_sp_probability
            )

            THEN("the extract time time series data returned is of the correct length")
            extract_time_ts = data.get("extract_time_ts")
            assert len(extract_time_ts) == number_records_processed
            for i, extract_time in enumerate(extract_time_ts):
                if i > 0:
                    THEN("the times in the series are ascending")
                    assert extract_time > extract_time_ts[i - 1]

            THEN(
                "the combined back size time series data returned is of the correct length"
            )
            combined_back_size_ts = data.get("combined_back_size_ts")
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
    THEN("the dataframe has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the dataframe has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


def test_removed_runner_df():
    GIVEN("the directory and file name of a test file which contains a removed runner")
    directory = "./data/29201704"
    file = "1.156695742.txt"
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()
    number_runners = __get_number_runners(data=raw_data)

    WHEN("we feed the data into a handler one record at a time")
    handler = DataHandler(adapter=RecordAdapter(), container=DataContainer())
    for i, raw_record in enumerate(raw_data):
        handler.add(raw_record)
        number_records_processed = i + 1
        THEN("the dataframe the correct number of records")
        assert handler._container.get_row_count() == number_records_processed

    WHEN("we have finished")
    THEN("the dataframe has the correct number of columns")
    assert handler._container.get_column_count() == __get_number_columns(number_runners)
    THEN("the dataframe has the same number of records as the raw data")
    assert handler._container.get_row_count() == len(raw_data)
    THEN("the correct number of runners are contained in the object")
    assert len(handler.get_unique_ids()) == number_runners


def __get_number_runners(data):
    return len(__get_runners(data))


def __get_runners(data):
    return data[0].get("marketInfo")[0].get("runners")


def __get_number_columns(number_runners):
    return (
        __get_number_columns_per_runner() * number_runners
    ) + __get_number_overarching_columns()


def __get_number_columns_per_runner():
    return 16


def __get_number_overarching_columns():
    return 1


from app.market.data.interface import ExternalAPIMarketDataInterface


class FakeAdapter(ExternalAPIMarketDataInterface):
    def convert(self, data):
        return data
