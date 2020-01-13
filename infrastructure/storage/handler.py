from infrastructure.built_in.adapter.json_utils import write_json_to, make_dict
from infrastructure.built_in.adapter.os_utils import (
    get_newline,
    get_file_path,
    path_exists,
    make_directory_if_required,
)


class FileHandler:
    def __init__(self, directory, file):
        self.__directory = directory
        self.__file = self.__add_path_to(file)
        self.__make_directory()

    def get_market_start_time(self):
        return self.get_file_as_list()[0].get("marketStartTime")

    def get_file_as_list(self):
        with open(self.__file, "r") as file:
            contents = [
                make_dict(line) for line in file.readlines() if self.__is_valid(line)
            ]
        return contents

    def get_file_as_formatted_list(self):
        return list(map(lambda item: self.__format_item(item), self.get_file_as_list()))

    def __format_item(self, item):
        formatted_item = item.get("marketInfo")[0]
        formatted_item["et"] = item.get("et")
        return formatted_item

    def __is_valid(self, line):
        return True if make_dict(line) else False

    def add_dict(self, dict):
        with open(self.__file, self.__write_type) as file:
            write_json_to(file=file, dict=dict)
            self.__add_new_line(file)
        return self.__file

    @property
    def __write_type(self):
        return "a" if self.__file_exists() else "w+"

    def __add_new_line(self, file):
        file.write(get_newline())
        return None

    def __make_directory(self):
        make_directory_if_required(self.__directory)
        return None

    def __add_path_to(self, file):
        return get_file_path(directory=self.__directory, file=file)

    def __file_exists(self):
        return path_exists(path=self.__file)
