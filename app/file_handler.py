from app.json_utils import write_json_to
from os import makedirs, linesep
from os.path import join
from app.os_utils import path_exists


class FileHandler:
    def __init__(self, directory, file):
        self.__directory = directory
        self.__file = self.__add_path_to(file)
        self.__make_directory() if not self.__directory_exists() else None

    def get_file_as_list(self):
        with open(self.__file, "r") as file:
            contents = list(file)
        return contents

    def add_dict(self, dict):
        with open(self.__file, self.__write_type) as file:
            write_json_to(file=file, dict=dict)
            self.__add_new_line(file)
        return self.__file

    @property
    def __write_type(self):
        return "a" if self.__file_exists() else "w+"

    def __add_new_line(self, file):
        file.write(linesep)
        return None

    def __make_directory(self):
        makedirs(self.__directory)
        return None

    def __add_path_to(self, file):
        return join(self.__directory, file)

    def __directory_exists(self):
        return path_exists(path=self.__directory)

    def __file_exists(self):
        return path_exists(path=self.__file)

    def __exists(self, path):
        return path_exists(path=path)
