from tests.utils import GIVEN, WHEN, THEN
from app.file_writer import FileWriter
from os import remove, rmdir
from json import loads
from os.path import exists

def test_file_writer():
    GIVEN("an instance of the FileWriter class and a basic dict")
    data_dir = "./test_data"
    file_writer = FileWriter(directory=data_dir, file="test.txt")
    first_dict = {"get me some": "wwweeeeeeeeeee"}
    second_dict = {"get me some more": "wwweeeeeeeeeeeeeeeeee"}

    WHEN("we call add_dict")
    test_file_path = file_writer.add_dict(first_dict)
    THEN("the file has been created")
    test_file = data_dir + "/test.txt"
    assert test_file_path == test_file
    assert exists(test_file) is True

    WHEN("we call add_dict again and open the file")
    test_file_path = file_writer.add_dict(second_dict)
    with open(test_file_path, "r") as f:
        l = list(f)
    THEN("the first list item is the first dict")
    assert loads(l[0]) == first_dict
    THEN("second list iten is the second dict")
    assert loads(l[1]) == second_dict

    remove(test_file)
    rmdir(data_dir)
