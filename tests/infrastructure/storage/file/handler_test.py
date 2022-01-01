from types import GeneratorType
from pytest import mark


from tests.utils import (
    GIVEN,
    WHEN,
    THEN,
    get_test_directory,
    cleanup_test_file,
)
from infrastructure.storage.file.handler import FileHandler
from infrastructure.built_in.adapter.os_utils import path_exists
from infrastructure.built_in.adapter.date_time import DateTime


def test_handler_test_file():
    GIVEN("an instance of the FileWriter class and a basic dict")
    data_dir = get_test_directory()
    test_file = "test_file_handler.txt"
    file_handler = FileHandler(directory=data_dir, file=test_file)
    first_dict = {"get me some": "wwweeeeeeeeeee"}
    second_dict = {"get me some more": "wwweeeeeeeeeeeeeeeeee"}
    empty_str = ""

    WHEN("we call add_dict")
    test_file_path = file_handler.add_dict(first_dict)

    THEN("the file has been created")
    assert path_exists(test_file_path) is True

    WHEN("we call add_dict again and open the file")
    test_file_path = file_handler.add_dict(second_dict)
    data = file_handler.get_file_as_list()

    THEN("the first list item is a json string of the first dict")
    assert data[0] == first_dict
    THEN("the second list item is a json string of the second dict")
    assert data[1] == second_dict

    WHEN("we call add_dict again for None and open the file")
    test_file_path = file_handler.add_dict(None)
    data = file_handler.get_file_as_list()

    THEN("the first list item is a json string of the first dict")
    assert data[0] == first_dict
    THEN("the second list item is a json string of the second dict")
    assert data[1] == second_dict
    THEN("None has not been returned as part of the list")
    assert len(data) == 2

    WHEN("we call add_dict for an empty string again and open the file")
    test_file_path = file_handler.add_dict(empty_str)
    data = file_handler.get_file_as_list()

    THEN("the first list item is a json string of the first dict")
    assert data[0] == first_dict
    THEN("the second list item is a json string of the second dict")
    assert data[1] == second_dict
    THEN("the empty string has not been returned as part of the list")
    assert len(data) == 2

    cleanup_test_file(name=test_file)


@mark.slow
def test_handler_download_file():
    GIVEN("a file and a directory with the correct market type")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler")
    file_data = FileHandler(directory=directory, file=file).get_file_as_list()

    THEN("it has loaded the file as a list")
    assert isinstance(file_data, list)

    THEN("the list has hundreds of records")
    assert len(file_data) > 200

    THEN("the list's first record has all of the items")
    first_record = file_data[0]
    items = first_record.get("mc")[0].get("marketDefinition").get("runners")
    assert isinstance(items, list)

    THEN("the list's first record has the market time")
    market_time = DateTime(
        first_record.get("mc")[0].get("marketDefinition").get("marketTime")
    ).get_epoch()
    assert market_time == 1569840120.0

    THEN("the first record has a process time which can be converted to an epoch")
    process_time = __get_record_process_time(first_record)
    assert isinstance(process_time, float)

    THEN("the process time is within 24 hours of the market_time")
    assert (market_time - process_time) < (60 * 60 * 24)

    THEN("the handler's file data has a last record")
    last_record = file_data[-1]

    THEN("the process time is after the market time but within 20 minutes")
    process_time = __get_record_process_time(last_record)
    assert (20 * 60) > -(market_time - process_time) > 0


@mark.slow
def test_get_file_as_generator():
    GIVEN("a file and a directory with the correct market type")
    directory = "./dev"
    file = "1.163093692.bz2"

    WHEN("we instantiate the handler")
    generator = FileHandler(directory=directory, file=file).get_file_as_generator()

    THEN("it has loaded the file as a generator")
    assert isinstance(generator, GeneratorType)

    THEN("the list's first record has all of the items")
    first_record = next(generator)
    items = first_record.get("mc")[0].get("marketDefinition").get("runners")
    assert isinstance(items, list)

    THEN("the list's first record has the market time")
    market_time = DateTime(
        first_record.get("mc")[0].get("marketDefinition").get("marketTime")
    ).get_epoch()
    assert market_time == 1569840120.0

    THEN("the first record has a process time which can be converted to an epoch")
    process_time = __get_record_process_time(first_record)
    assert isinstance(process_time, float)

    THEN("the process time is within 24 hours of the market_time")
    assert (market_time - process_time) < (60 * 60 * 24)

    THEN("the list has hundreds of records")
    map(lambda: ___test_call(generator), range(200))

    THEN("the handler's file data has a last record")
    last_record = list(generator)[-1]

    THEN("the process time is after the market time but within 20 minutes")
    process_time = __get_record_process_time(last_record)
    assert (20 * 60) > -(market_time - process_time) > 0


def ___test_call(generator):
    record = next(generator)
    assert isinstance(record, dict)


def __get_record_process_time(record):
    return DateTime(record.get("pt")).get_epoch()
