from app.market.data.utils import try_divide


class PriceHandler:
    def __init__(self, discount_rate=0):
        self.__discount_rate = discount_rate

    def set_discount_rate(self, discount_rate):
        self.__discount_rate = discount_rate

    def calc_discounted_probability(self, price):
        return self.calc_probability(self.remove_commission(price))

    def remove_commission(self, price):
        return self.__calc_profit(price=price) + 1

    def calc_probability(self, price):
        return self.__invert(price)

    def calc_price(self, probability):
        return self.__invert(probability)

    def __invert(self, value):
        return try_divide(value=1, denominator=value)

    def __calc_profit(self, price):
        return (price - 1) * (self.__percentage_after_commission())

    def __percentage_after_commission(self):
        return 1 - self.__calc_comission_percentage()

    def __calc_comission_percentage(self):
        return 0.05 * (1 - self.__discount_rate)
