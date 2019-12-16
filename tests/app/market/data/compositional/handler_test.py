from tests.utils import GIVEN, WHEN, THEN
from app.market.data.compositional.handler import CompositionalDataHandler


def test_create_comp_data():
    GIVEN("a simple set of data and a compositional_data_handler")
    items = {"id": 123, "sp_back_price": 2.1}, {"id": 456, "sp_back_price": 2.1}
    handler = CompositionalDataHandler(
        items=items, price_name="sp_back_price", correct_probability=1
    )
    WHEN("we call calc_compositional_data")
    cdf = handler.calc_compositional_data()
    THEN("a dataframe with the correct results is returned")
    assert cdf == [
        {
            "id": 123,
            "adj_price": (1.1 * 0.95) + 1,
            "probability": 1 / ((1.1 * 0.95) + 1),
            "compositional_probability": 0.5,
            "compositional_price": 2,
        },
        {
            "id": 456,
            "adj_price": (1.1 * 0.95) + 1,
            "probability": 1 / ((1.1 * 0.95) + 1),
            "compositional_probability": 0.5,
            "compositional_price": 2,
        },
    ]
