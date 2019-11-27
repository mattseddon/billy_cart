from tests.utils import GIVEN, WHEN, THEN, get_test_file_path, cleanup_test_file
from app.third_party_adapter.json_utils import write_json_to, make_dict


def test_json_utils():
    GIVEN("an open file and a dict")

    test_file = "test_write_to_json.txt"
    test_file_path = get_test_file_path(name=test_file)
    test_dict = {"this is a silly": "dict", "it would have no use": True}

    with open(test_file_path, "w+") as file:
        WHEN("we write the dict as json to the file")
        write_json_to(file=file, dict=test_dict)

    THEN("the record is in the file and can be converted back into the dict")
    with open(test_file_path, "r") as file:
        json_string = list(file)[0]
    assert make_dict(json_string) == test_dict

    cleanup_test_file(name=test_file)

def test_make_dict():
    GIVEN("valid dictionary in a json string")
    string = 'this is clearly not a json dictionary'

    WHEN("we call make_dict")
    dict = make_dict(string)

    THEN("None is returned")
    assert dict is None