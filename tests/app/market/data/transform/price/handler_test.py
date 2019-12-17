from tests.utils import GIVEN, WHEN, THEN
from app.market.data.transform.price.handler import PriceHandler


def test_remove_commission():
    GIVEN("a price and the returns handler")
    handler = PriceHandler()
    prices = [2.1, 1.05, 95, 75.1, 4.6, 9.1]

    for price in prices:
        WHEN("we calculate the return of the offered price")
        price_minus_commission = handler.remove_commission(price=price)
        commission_on_profit = 0.05
        profit = price - 1

        THEN("the correct price is returned")
        assert price_minus_commission == ((profit) * (1 - commission_on_profit)) + 1


def test_remove_commission_with_discount():
    GIVEN("a price and the returns handler with a discount rate")
    discount_rate = 0.1
    handler = PriceHandler(discount_rate=discount_rate)
    prices = [2.1, 1.05, 95, 75.1, 4.6, 9.1]

    for price in prices:
        WHEN("we calculate the return of the offered price")
        price_minus_commission = handler.remove_commission(price=price)
        commission_on_profit = 0.05 * (1 - discount_rate)
        profit = price - 1

        THEN("the correct price is returned")
        assert price_minus_commission == ((profit) * (1 - commission_on_profit)) + 1


def test_calc_probability():
    GIVEN("a price handler and a price")
    handler = PriceHandler()
    price = 2

    WHEN("we calculate the associated probability")
    probability = handler.calc_probability(price=price)

    THEN("the correct probability is returned")
    assert probability == 0.5


def test_calc_discounted_probability():
    GIVEN("a price handler and a price")
    handler = PriceHandler()
    price = 2
    commission_on_profit = 0.05
    profit = price - 1

    WHEN("we calculate the probability of the price minus the commission")
    probability = handler.calc_discounted_probability(price=price)

    THEN("the correct probability is returned")
    assert probability == 1 / (((profit) * (1 - commission_on_profit)) + 1)
