from os import environ, makedirs, remove, rmdir
from os.path import exists

def GIVEN(str):
    print("\nGIVEN {}".format(str))


def WHEN(str):
    print("    WHEN {}".format(str))


def THEN(str):
    print("        THEN {}".format(str))


def should_test_real_api():
    should = True if environ.get("test_suite") == "online" else False
    return should

def get_test_dir_path():
    return './test_data'

def get_test_file_path(name):
    dir_path = __make_test_dir()
    file_path = dir_path + '/' + name if dir_path else None
    return file_path

def __make_test_dir():
    test_dir = get_test_dir_path()
    if not exists(test_dir):
        makedirs(test_dir)
    path = test_dir if exists(test_dir) else None
    return path

def cleanup_test_file(name):
    test_dir = get_test_dir_path()
    file_path = test_dir + '/' + name
    remove(file_path)
    rmdir(test_dir)
