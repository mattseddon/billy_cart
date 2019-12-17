class CompositionalDataHandler:
    def __init__(self, items, price_name, correct_probability):
        self.__items = items
        self.__correct_probability = correct_probability
        self.__price_name = price_name

    def calc_compositional_data(self):

        compositional_items = list(
            map(lambda item: self.__calc_adjusted_values(item=item), self.__items)
        )

        self.__total_probability = sum(
            item.get("probability") for item in compositional_items
        )

        compositional_items = list(
            map(
                lambda item: self.__calc_compositional_values(item=item),
                compositional_items,
            )
        )

        return compositional_items

    def __calc_adjusted_values(self, item):
        data = {}
        data["id"] = item.get("id")
        data["adj_price"] = self.__calc_total_return(price=item.get(self.__price_name))
        data["probability"] = self.__calc_probability(data.get("adj_price"))
        return data

    def __calc_compositional_values(self, item):
        item["compositional_probability"] = (
            self.__correct_probability
            / self.__total_probability
            * item.get("probability")
        )
        item["compositional_price"] = self.__calc_probability(
            item.get("compositional_probability")
        )
        return item

    def __calc_probability(self, price):
        return 1 / price

    def __calc_total_return(self, price):
        return self.__calc_return(price) + 1

    # this will need to go into the business rules
    def __calc_return(self, price):
        return (price - 1) * (1 - self.__calc_comission_percentage())

    def __calc_comission_percentage(self, discount_rate=0):
        return 0.05 * (1 - discount_rate)
