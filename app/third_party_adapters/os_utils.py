from os import environ, linesep, makedirs, remove, rmdir
from os.path import exists, join


def path_exists(path):
    return exists(path)


def get_file_path(directory, file):
    return join(directory, file)


def get_newline():
    return linesep


def make_directory_if_required(path):
    if not exists(path):
        makedirs(path)
    return path if exists(path) else None


def remove_directory(path):
    if exists(path):
        rmdir(path)
    return __confirm_path_removed(path)


def remove_file(path):
    if exists(path):
        remove(path)
    return __confirm_path_removed(path)


def get_environment_variable(variable):
    return environ.get(variable)


def set_environment_variable(variable, value):
    environ[variable] = value
    return None


def __confirm_path_removed(path):
    return None if not exists(path) else path
