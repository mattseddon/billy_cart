from tests.utils import GIVEN, WHEN, THEN, get_test_directory, cleanup_test_file
from app.file_handler import FileHandler
from app.third_party_adapters.json_utils import make_dict
from app.third_party_adapters.os_utils import path_exists


def test_file_handler():
    GIVEN("an instance of the FileWriter class and a basic dict")
    data_dir = get_test_directory()
    test_file = "test_file_handler.txt"
    file_handler = FileHandler(directory=data_dir, file=test_file)
    first_dict = {"get me some": "wwweeeeeeeeeee"}
    second_dict = {"get me some more": "wwweeeeeeeeeeeeeeeeee"}

    WHEN("we call add_dict")
    test_file_path = file_handler.add_dict(first_dict)

    THEN("the file has been created")
    assert path_exists(test_file_path) is True

    WHEN("we call add_dict again and open the file")
    test_file_path = file_handler.add_dict(second_dict)
    data = file_handler.get_file_as_list()

    THEN("the first list item is a json string of the first dict")
    assert make_dict(data[0]) == first_dict
    THEN("the second list item is a json string of the second dict")
    assert make_dict(data[1]) == second_dict

    cleanup_test_file(name=test_file)
