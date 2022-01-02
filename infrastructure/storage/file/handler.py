import bz2

from infrastructure.built_in.adapter.json_utils import write_json_to, make_dict
from infrastructure.built_in.adapter.os_utils import (
    get_newline,
    get_file_extension,
    get_file_path,
    path_exists,
    make_directory_if_required,
)


class FileHandler:
    def __init__(self, directory, file):
        self.__directory = directory
        self.__file = self.__add_path_to(file)
        self.__make_directory()

    def get_file_as_generator(self):
        if get_file_extension(self.__file) == ".bz2":
            yield from self.__get_bz2_contents()
        else:
            yield from self.__get_file_contents()

    def get_file_as_list(self):
        if get_file_extension(self.__file) == ".bz2":
            return self.__get_bz2_contents()

        return self.__get_file_contents()

    def __get_bz2_contents(self):
        with bz2.open(self.__file, "r") as file:
            contents = self.__get_contents(file)
        return contents

    def __get_file_contents(self):
        with open(self.__file, "r", encoding="utf-8") as file:
            contents = self.__get_contents(file)
        return contents

    def __get_contents(self, file):
        return [make_dict(line) for line in file.readlines() if self.__is_valid(line)]

    def __is_valid(self, line):
        return True if make_dict(line) else False

    def get_first_record(self):
        if get_file_extension(self.__file) == ".bz2":
            return self.__get_first_bz2_record()
        return self.__get_first_record()

    def __get_first_bz2_record(self):
        with bz2.open(self.__file, "r") as file:
            return make_dict(next(file))

    def __get_first_record(self):
        with open(self.__file, "r", encoding="utf-8") as file:
            return make_dict(next(file))

    def add_dict(self, data):
        with open(self.__file, self.__write_type, encoding="utf-8") as file:
            write_json_to(file=file, data=data)
            self.__add_new_line(file)
        return self.__file

    @property
    def __write_type(self):
        return "a" if self.__file_exists() else "w+"

    def __add_new_line(self, file):
        file.write(get_newline())

    def __make_directory(self):
        make_directory_if_required(self.__directory)

    def __add_path_to(self, file):
        return get_file_path(directory=self.__directory, file=file)

    def __file_exists(self):
        return path_exists(path=self.__file)
