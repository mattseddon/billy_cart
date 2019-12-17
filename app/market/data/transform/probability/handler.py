from app.market.data.utils import is_a_number


class ProbabilityHandler:
    def __init__(self, items, name, correct_probability):
        self.__items = items
        self.__correct_probability = correct_probability
        self.__name = name

    def calc_compositional_probabilities(self):

        self.__total_probability = sum(
            item.get(self.__name)
            for item in self.__items
            if is_a_number(item.get(self.__name))
        )

        compositional_items = list(
            map(
                lambda item: self.__calc_compositional_probability(item=item),
                self.__items,
            )
        )

        return compositional_items

    def __calc_compositional_probability(self, item):
        compositional_item = {"id": item.get("id")}
        compositional_item["compositional_probability"] = (
            self.__correct_probability
            / self.__total_probability
            * item.get(self.__name)
        )
        return compositional_item
