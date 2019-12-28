from app.market.data.transform.probability.handler import ProbabilityHandler
from app.market.data.transform.price.handler import PriceHandler
from app.market.metadata.handler import MetadataHandler


class TransformHandler:
    def __init__(self, total_probability=1):
        self.__pricer = PriceHandler()
        self.__metadata = MetadataHandler()
        self.__total_probability = total_probability
        self.__remaining_probability = total_probability
        self.__probabilities = {}

    def set_probability(self, id, probability):
        self.__probabilities[id] = probability
        return None

    def get_fixed_probability_ids(self):
        return list(self.__probabilities.keys())

    def process(self, extracted_data={}):
        items = extracted_data.get("items") or []
        extract_time = extracted_data.get("extract_time")
        closed_indicator = extracted_data.get("closed_indicator")

        self.__transformed_data = {}
        self._set_items(items=items)
        self._set_extract_time(extract_time=extract_time)
        self._set_closed_indicator(closed_indicator=closed_indicator)
        self._calc_remaining_probability()

        if self.__is_valid_record():
            self.__add_extract_time()
            self.__add_closed_indicator()
            self.__add_default_data()
            self.__add_adj_back_prices()
            self.__add_combined_back_size()
            self.__add_compositional_sp_data()
            self.__add_compositional_ex_data()
            self.__add_market_back_size()

        return self.__transformed_data

    def _set_items(self, items):
        self.__items = self._exclude_fixed_items(items=items)
        return None

    def _exclude_fixed_items(self, items):
        return list(
            filter(
                lambda item: item.get("id") not in self.get_fixed_probability_ids(),
                items,
            )
        )

    def _set_extract_time(self, extract_time):
        self.__extract_time = extract_time
        return None

    def _set_closed_indicator(self, closed_indicator):
        self.__closed_indicator = closed_indicator
        return None

    def _calc_remaining_probability(self):
        self.__remaining_probability = self.__total_probability - sum(
            self.__probabilities.values()
        )
        return None

    def __is_valid_record(self):
        return self.__items and self.__extract_time is not None

    def __add_extract_time(self):
        self.__transformed_data[("extract_time", "")] = [self.__extract_time]
        return None

    def __add_closed_indicator(self):
        self.__transformed_data[("closed_indicator", "")] = [
            self.__closed_indicator and self.__extract_time >= 0
        ]

    def __add_default_data(self):
        for column in self.__metadata.get_required_variables():
            for item in self.__items:
                self.__transformed_data[
                    self.__get_composite_column_name(variable=column, item=item)
                ] = [item.get(column)]
        return None

    def __add_adj_back_prices(self):
        for column in self.__metadata.get_back_prices():
            for item in self.__items:
                self.__transformed_data[
                    self.__get_composite_column_name(
                        variable=(
                            column + self.__metadata.get_minus_commission_suffix()
                        ),
                        item=item,
                    )
                ] = [self.__pricer.remove_commission(item.get(column))]
        return None

    def __add_combined_back_size(self):
        for item in self.__items:
            combined_back_size = sum(
                item.get(size) for size in self.__metadata.get_back_sizes()
            )
            self.__transformed_data[
                self.__get_composite_column_name(
                    variable="combined_back_size", item=item
                )
            ] = [combined_back_size]
        return None

    def __add_compositional_sp_data(self):
        self.__add_compositional_data(name="sp")
        return None

    def __add_compositional_ex_data(self):
        self.__add_compositional_data(name="ex_average")
        return None

    def __add_compositional_data(self, name):
        compositional_data = self._get_compositional_data(
            price_name=(name + "_back_price")
        )

        for item in compositional_data:
            self.__transformed_data[
                self.__get_composite_column_name(
                    variable="compositional_" + name + "_probability", item=item
                )
            ] = [item.get("compositional_probability")]

            self.__transformed_data[
                self.__get_composite_column_name(
                    variable="compositional_" + name + "_back_price", item=item
                )
            ] = [item.get("compositional_price")]

        return None

    def __add_market_back_size(self):
        self.__transformed_data[("market_back_size", "")] = [
            sum(
                item.get(size)
                for size in self.__metadata.get_back_sizes()
                for item in self.__items
            )
        ]
        return None

    def __get_composite_column_name(self, variable, item):
        return (variable, item.get("id"))

    def _get_compositional_data(self, price_name):

        probabilities = list(
            map(
                lambda item: self.__calc_initial_probability(
                    item=item, price_name=price_name
                ),
                self.__items,
            )
        )

        probability_handler = ProbabilityHandler(
            items=probabilities,
            name="probability",
            correct_probability=self.__remaining_probability,
        )
        compositional_probabilities = (
            probability_handler.calc_compositional_probabilities()
        )

        compositional_data = list(
            map(
                lambda item: self.__add_compositional_price(item),
                compositional_probabilities,
            )
        )

        return compositional_data

    def __calc_initial_probability(self, item, price_name):

        probability = {
            "id": item.get("id"),
            "probability": self.__pricer.calc_discounted_probability(
                item.get(price_name)
            ),
        }
        return probability

    def __add_compositional_price(self, item):
        item["compositional_price"] = self.__pricer.calc_price(
            item.get("compositional_probability")
        )
        return item
