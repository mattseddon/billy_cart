from app.market.data.compositional.handler import CompositionalDataHandler


class DataHandler:
    def __init__(self, adapter, container):
        self._container = container.new()
        self.__adapter = adapter
        self.__probabilities = {}

    def add(self, data):

        transformed_data = self._transform(data=data)
        if transformed_data:
            record_container = self._container.new(transformed_data)
            record_container.set_index(("extract_time", ""))
            record_container.set_column_group_name(names=["variable", "id"])
            # if self.__probabilities then (override probabilities) or (miss the item completely)
            record_container.sum_columns(
                output="market_back_size", columns=["ex_back_size", "sp_back_size"]
            )
            # when creating the compositional probs will need to take into account any static ones
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

    def _transform(self, data):
        adapted_data = self.__adapter.convert(data)
        items = adapted_data.get("items") or []

        compositional_sp_back_data = self.__get_compositional_data(
            items=items, price_name="sp_back_price"
        )

        compositional_ex_back_data = self.__get_compositional_data(
            items=items, price_name="ex_average_back_price"
        )

        transformed_data = self.__make_initial_transformed_dict(items=items)

        transformed_data.update(
            {
                self.__get_composite_column_name(
                    variable="combined_back_size", item=item
                ): [item.get("ex_back_size") + item.get("sp_back_size")]
                for item in items
            }
        )

        transformed_data.update(
            self.__make_transformed_dict(
                out_column="compositional_sp_probability",
                items=compositional_sp_back_data,
                in_column="compositional_probability",
            )
        )

        transformed_data.update(
            self.__make_transformed_dict(
                out_column="compositional_sp_back_price",
                items=compositional_sp_back_data,
                in_column="compositional_price",
            )
        )

        transformed_data.update(
            self.__make_transformed_dict(
                out_column="compositional_ex_probability",
                items=compositional_ex_back_data,
                in_column="compositional_probability",
            )
        )

        transformed_data.update(
            self.__make_transformed_dict(
                out_column="compositional_ex_back_price",
                items=compositional_ex_back_data,
                in_column="compositional_price",
            )
        )

        if transformed_data:
            transformed_data[("extract_time", "")] = adapted_data.get("extract_time")

        return transformed_data

    def __make_initial_transformed_dict(self, items):
        intial_data = {}
        for column in self.__get_column_list():
            intial_data.update(
                self.__make_transformed_dict(out_column=column, items=items)
            )
        return intial_data

    def __make_transformed_dict(self, out_column, items, in_column=None):
        if not (in_column):
            in_column = out_column
        return {
            self.__get_composite_column_name(variable=out_column, item=item): [
                item.get(in_column)
            ]
            for item in items
        }

    def __get_column_list(self):
        return [
            "removal_date",
            "sp_back_price",
            "sp_back_size",
            "sp_lay_price",
            "sp_lay_size",
            "ex_average_back_price",
            "ex_back_size",
            "ex_average_lay_price",
            "ex_lay_size",
            "ex_offered_back_price",
            "ex_offered_lay_price",
        ]

    def __get_composite_column_name(self, variable, item):
        return (variable, item.get("id"))

    def __get_compositional_data(self, items, price_name, correct_probability=1):
        compositional_data_handler = CompositionalDataHandler(
            items=items, price_name=price_name, correct_probability=1,
        )
        compositional_items = compositional_data_handler.calc_compositional_data()
        return compositional_items

    def __get_item_model_data(self, id):
        data = {}
        data["id"] = id
        data["combined_back_size"] = self._container.get_last_column_entry(
            name=("combined_back_size", id)
        )
        data["compositional_sp_probability"] = self._container.get_last_column_entry(
            name=("compositional_sp_probability", id)
        )
        data["compositional_ex_probability"] = self._container.get_last_column_entry(
            name=("compositional_ex_probability", id)
        )
        data["ex_offered_back_price"] = self._container.get_last_column_entry(
            name=("ex_offered_back_price", id)
        )

        data["compositional_sp_back_price_ts"] = self._container.get_column(
            name=("compositional_sp_back_price", id)
        )

        data["extract_time_ts"] = self._container.get_index()

        data["combined_back_size_ts"] = self._container.get_column(
            name=("combined_back_size", id)
        )
        return data
