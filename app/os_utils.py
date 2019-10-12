from os import environ, linesep, makedirs, remove, rmdir
from os.path import exists

def get_environment_variable(variable):
    return environ.get(variable)

def set_environment_variable(variable,value):
    environ[variable] = value
    return None

def path_exists(path):
    return exists(path)