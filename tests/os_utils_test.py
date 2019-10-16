from tests.utils import GIVEN, WHEN, THEN, get_test_file_path, cleanup_test_directory
from third_party_adapters.os_utils import (
    get_file_path,
    get_newline,
    get_environment_variable,
    set_environment_variable,
    path_exists,
    make_directory_if_required,
    remove_directory,
    remove_file,
)


def test_get_environment_variable():
    GIVEN("a Test environment variable")
    variable = "Test"
    set_environment_variable(variable=variable, value="Pass")

    WHEN("we retrieve it")
    Test = get_environment_variable(variable=variable)

    THEN("the correct variable value is returned")
    assert Test == "Pass"

    GIVEN("no environment variable")

    WHEN("we retrieve it")
    Test = get_environment_variable(variable=" ")

    THEN("the correct variable value is returned")
    assert Test == None


def test_path_exists():
    GIVEN("a valid existing path")
    path = "./"

    WHEN("we check to see if the path exists")
    exists = path_exists(path=path)

    THEN("it does")
    assert exists == True

    GIVEN("an invalid and non-existent path")
    path = "./wwwwwwwweeeeeeeeeeeeee/wwwwweeeeeeeeeeee/wwwwwwwweeeeeeeee"

    WHEN("we check to see if the path exists")
    exists = path_exists(path=path)

    THEN("it does")
    assert exists == False


def test_get_newline():
    GIVEN("a newline")
    newline_str = "\n"
    WHEN("we get a newline")
    newline = get_newline()
    THEN("they are the same")
    assert newline == newline_str


def test_make_directory():
    GIVEN("a path")
    path = "./test_make_directories"
    WHEN("we check if the path exists")
    exists = path_exists(path=path)
    THEN("it does not")
    assert exists == False
    WHEN("we make the directory and check if it now exists")
    returned_path = make_directory_if_required(path=path)
    exists = path_exists(path=path)
    THEN("it does")
    assert exists == True
    assert returned_path == path
    remove_directory(path)


def test_remove_directory():
    GIVEN("an empty directory")
    path = "./test_remove_directory"
    make_directory_if_required(path=path)

    WHEN("we try to remove the directory and check for existence")
    returned_path = remove_directory(path)
    exists = path_exists(path=path)

    THEN("it is removed")
    assert exists == False
    assert returned_path == None


def test_remove_file():
    GIVEN("a file")
    name = "test_remove_file.txt"
    test_file_path = get_test_file_path(name=name)
    f = open(test_file_path, "w+")
    f.close()

    WHEN("we check that the file exists")
    exists = path_exists(path=test_file_path)

    THEN("it does")
    assert exists == True

    WHEN("we remove the file and check for existence")
    remove_file(path=test_file_path)
    exists = path_exists(path=test_file_path)

    THEN("it has been remove")
    assert exists == False

    cleanup_test_directory()


def test_get_file_path():
    GIVEN("a file name and a directory")
    name = "made_up_file_name.txt"
    directory = "./made/up/folder/structure"

    WHEN("we get the file path")
    returned_path = get_file_path(directory=directory, file=name)
    joined_path = directory + "/" + name

    THEN("the returned path is correct")
    assert returned_path == joined_path
