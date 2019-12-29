from app.colleague import Colleague

from app.market.data.transform.handler import TransformHandler
from app.market.metadata.handler import MetadataHandler


class DataHandler(Colleague):
    def __init__(self, mediator, adapter, container, transformer=None):
        self._container = container.new()
        self.__extractor = adapter
        self.__transformer = transformer or TransformHandler()
        self.__metadata = MetadataHandler()
        self.__consecutive_empty_data = 0
        Colleague.__init__(self, mediator=mediator)

    def process_data(self, data):

        container_size = self.__get_container_size()
        extracted_data = self._extract(data=data)
        if not (extracted_data):
            self.__consecutive_empty_data += 1
            return (
                self._mediator.notify(event="finished processing")
                if self.__consecutive_empty_data < 10
                else self._mediator.notify(event="no data provided multiple times")
            )

        transformed_data = self._transform(extracted_data=extracted_data)
        if transformed_data:
            self.__add_to_container(data=transformed_data)

        if self._confirm_market_closed():
            return self._mediator.notify(event="market closed")

        if self.__container_expanded(container_size):
            self.__consecutive_empty_data = 0
            return self._mediator.notify(
                event="data added to container", data=self._get_model_data()
            )

    def fix_probabilities(self, items):
        for item in items:
            self._set_probability(
                id=item.get("id"), probability=item.get("probability")
            )

    def _confirm_market_closed(self):
        closed_indicator = ("closed_indicator", "")
        return (
            self._container.get_last_column_entry(name=closed_indicator)
            if self._container.has_column(closed_indicator)
            else 0
        )

    def _get_model_data(self):
        model_data = list(
            map(
                lambda id: self.__get_item_model_data(id),
                self._get_ids_for_model_data(),
            )
        )
        return model_data

    def _get_ids_for_model_data(self):
        return list(
            filter(
                lambda id: not id in self._get_fixed_probability_ids(),
                self.get_unique_ids(),
            )
        )

    def _get_fixed_probability_ids(self):
        return self.__transformer.get_fixed_probability_ids()

    def _set_probability(self, id, probability):
        self.__transformer.set_probability(id=id, probability=probability)
        return None

    def get_unique_ids(self):
        index = self._container.get_column_group_values(name="id")
        return [id for id in index if type(id) is int]

    def _extract(self, data):
        extracted_data = self.__extractor.convert(data)
        return extracted_data

    def _transform(self, extracted_data):
        transformed_data = self.__transformer.process(extracted_data)
        return transformed_data

    def __add_to_container(self, data):
        record_container = self._container.new(data=data)
        record_container.set_index((self.__metadata.get_index_name(), ""))
        record_container.set_column_group_name(names=["variable", "id"])
        self._container.add_rows(container=record_container)

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
