from infrastructure.built_in.adapter.os_utils import (
    get_environment_variable,
    get_file_path,
    make_directory_if_required,
    path_exists,
    remove_directory,
    remove_file,
)


def GIVEN(str):
    print("\nGIVEN {}".format(str))


def WHEN(str):
    print("    WHEN {}".format(str))


def THEN(str):
    print("        THEN {}".format(str))


def get_test_directory():
    return "./test_data"


def get_test_file_path(name):
    directory = __make_test_directory()
    file_path = get_file_path(directory=directory, file=name) if directory else None
    return file_path


def lists_are_equal(first, second):
    return len(first) == len(second) and sorted(first) == sorted(second)


def almost_equal(first, second):
    return abs((first) - (second)) < 0.0000001


def __make_test_directory():
    directory = get_test_directory()
    path = make_directory_if_required(directory)
    return path


def cleanup_test_file(name):
    directory = get_test_directory()
    path = get_file_path(directory=directory, file=name)
    file_exists = remove_file(path=path)
    directory_exists = cleanup_test_directory()
    return True if not (directory_exists or file_exists) else False


def cleanup_test_directory():
    directory = get_test_directory()
    directory_exists = remove_directory(directory)
    return True if not directory_exists else False
