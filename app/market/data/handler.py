from app.market.data.transform.handler import TransformHandler
from app.market.metadata.handler import MetadataHandler


class DataHandler:
    def __init__(self, adapter, container, transformer=TransformHandler()):
        self._container = container.new()
        self.__extractor = adapter
        self.__transformer = transformer
        self.__probabilities = {}
        self.__metadata = MetadataHandler()

    def add(self, data):

        container_size = self.__get_container_size()
        extracted_data = self._extract(data=data)
        transformed_data = self._transform(extracted_data=extracted_data)
        if transformed_data:
            record_container = self._container.new(data=transformed_data)
            record_container.set_index((self.__metadata.get_index_name(), ""))
            record_container.set_column_group_name(names=["variable", "id"])
            # if self.__probabilities then (override probabilities) or (miss the item completely)
            # when creating the compositional probabilities will need to take into account any static ones
            # if item has 60% then rest should sum to 40%
            self._container.add_rows(container=record_container)

        return 1 if self.__container_expanded(container_size) else 0

    def confirm_market_closed(self):
        closed_indicator = ("closed_indicator", "")
        return (
            self._container.get_last_column_entry(name=closed_indicator)
            if self._container.has_column(closed_indicator)
            else 0
        )

    def get_model_data(self):
        ids = self.get_unique_ids()
        model_data = list(map(lambda id: self.__get_item_model_data(id), ids))
        return model_data

    def set_probability(self, id, probability):
        self.__probabilities[id] = probability
        return None

    def get_probability(self, id):
        return self.__probabilities.get(id)

    def get_unique_ids(self):
        index = self._container.get_column_group_values(name="id")
        return [id for id in index if type(id) is int]

    def _extract(self, data):
        extracted_data = self.__extractor.convert(data)
        return extracted_data

    def _transform(self, extracted_data):
        transformed_data = self.__transformer.process(extracted_data)
        return transformed_data

    def __get_container_size(self):
        return self._container.get_row_count() * self.__get_container_column_count()

    def __get_container_column_count(self):
        return self._container.get_column_count()

    def __container_expanded(self, original_size):
        return self.__get_container_size() == (
            original_size + self.__get_container_column_count()
        )

    def __get_item_model_data(self, id):
        data = {
            "id": id,
            self.__metadata.get_index_name()
            + self.__metadata.get_time_series_suffix(): self._container.get_index(),
        }

        data.update(
            {
                column
                + self.__metadata.get_point_in_time_suffix(): self._container.get_last_column_entry(
                    name=(column, id)
                )
                for column in self.__metadata.get_point_in_time_model_variables()
            }
        )

        data.update(
            {
                column
                + self.__metadata.get_time_series_suffix(): self._container.get_column(
                    name=(column, id)
                )
                for column in self.__metadata.get_time_series_model_variables()
            }
        )

        return data
