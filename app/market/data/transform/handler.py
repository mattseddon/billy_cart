from app.market.data.transform.probability.handler import ProbabilityHandler
from app.market.data.transform.price.handler import PriceHandler


class TransformHandler:
    def __init__(self):
        self.__pricer = PriceHandler()

    def set_items(self, items):
        self.__items = items

    def process(self, items):
        self.set_items(items=items)

        self.__transformed_data = {}
        self.__add_default_data()
        self.__add_combined_back_size()
        self.__add_compositional_sp_data()
        self.__add_compositional_ex_data()

        return self.__transformed_data

    def __add_default_data(self):
        for column in self.__get_column_list():
            for item in self.__items:
                self.__transformed_data[
                    self.__get_composite_column_name(variable=column, item=item)
                ] = [item.get(column)]
        return None

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
        ]  # all prices should be adjusted as they come in here instead of elsewhere in the app - use price handler
        # move this into metadata folder

    def __add_combined_back_size(self):
        for item in self.__items:
            self.__transformed_data[
                self.__get_composite_column_name(
                    variable="combined_back_size", item=item
                )
            ] = [item.get("ex_back_size") + item.get("sp_back_size")]

    def __add_compositional_sp_data(self):
        self.__add_compositional_data(name="sp")
        return None

    def __add_compositional_ex_data(self):
        self.__add_compositional_data(name="ex_average")
        return None

    def __add_compositional_data(self, name):
        compositional_data = self.__get_compositional_probabilities(
            items=self.__items, price_name=(name + "_back_price")
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

    def __get_composite_column_name(self, variable, item):
        return (variable, item.get("id"))

    def __get_compositional_probabilities(
        self, items, price_name, correct_probability=1
    ):

        probabilities = list(
            map(lambda item: self.__calc_initial_probability(item, price_name), items)
        )

        probability_handler = ProbabilityHandler(
            items=probabilities,
            name="probability",
            correct_probability=correct_probability,
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
