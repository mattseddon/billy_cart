from tests.utils import GIVEN, WHEN, THEN, get_test_directory, cleanup_test_file
from infrastructure.storage.handler import FileHandler
from infrastructure.built_in.adapter.os_utils import path_exists, get_newline


def test_file_handler():
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
