from infrastructure.storage.file.handler import FileHandler


class HistoricalExternalAPIFileHander(FileHandler):
    def __init__(self, directory, file):
        super().__init__(directory=directory, file=file)
        self.__file_data = super().get_file_as_list()

    def get_market_start_time(self):
        return self.__file_data[0].get("marketStartTime")

    def get_file_as_list(self):
        return list(map(self.__format_item, self.__file_data))

    def __format_item(self, item):
        formatted_item = item.get("marketInfo")[0]
        formatted_item["process_time"] = item.get("et")
        return formatted_item
