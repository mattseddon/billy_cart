from app.market.data.transform.handler import TransformHandler


class DataHandler:
    def __init__(self, adapter, container):
        self._container = container.new()
        self.__extractor = adapter
        self.__transformer = TransformHandler()
        self.__probabilities = {}

    def add(self, data):

        extracted_data = self._extract(data=data)
        transformed_data = self._transform(extracted_data=extracted_data)
        if transformed_data:
            record_container = self._container.new(data=transformed_data)
            record_container.set_index(("extract_time", ""))
            record_container.set_column_group_name(names=["variable", "id"])
            # if self.__probabilities then (override probabilities) or (miss the item completely)
            record_container.sum_columns(
                output="market_back_size", columns=["ex_back_size", "sp_back_size"]
            )
            # when creating the compositional probabilities will need to take into account any static ones
            # if item has 60% then rest should sum to 40%
            self._container.add_rows(container=record_container)

        return None

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
        items = extracted_data.get("items") or []
        transformed_data = self.__transformer.process(items)
        if transformed_data:
            transformed_data[("extract_time", "")] = extracted_data.get("extract_time")
        return transformed_data

    def __get_item_model_data(self, id):
        data = {
            "id": id,
            "extract_time_ts": self._container.get_index(),
        }

        data.update(
            {
                column: self._container.get_last_column_entry(name=(column, id))
                for column in [
                    "combined_back_size",
                    "compositional_sp_probability",
                    "compositional_ex_average_probability",
                    "ex_offered_back_price",
                ]
            }
        )

        data.update(
            {
                column + "_ts": self._container.get_column(name=(column, id))
                for column in ["compositional_sp_back_price", "combined_back_size"]
            }
        )

        return data
