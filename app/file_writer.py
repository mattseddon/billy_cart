from json import dump
from os import makedirs, linesep
from os.path import exists, join


class FileWriter:
    def __init__(self, directory, file):
        self.__directory = directory
        self.__file = self.__add_path_to(file)
        self.__make_directory()
        self.__write_type = "a" if self.__file_exists else "w+"

    def add_dict(self, dict):
        with open(self.__file, self.__write_type) as file:
            self.__write(dict, file)
            self.__add_new_line(file)
        return self.__file

    def __write(self,dict,file):
        dump(dict,file)
        return None

    def __add_new_line(self,file):
        file.write(linesep)
        return None

    def __make_directory(self):
        if not self.__directory_exists():
            makedirs(self.__directory)
        return None

    def __add_path_to(self,file):
        return join(self.__directory,file)

    def __directory_exists(self):
        return self.__exists(self.__directory)

    def __file_exists(self):
        return self.__exists(self.__file)

    def __exists(self,path):
        return exists(path)