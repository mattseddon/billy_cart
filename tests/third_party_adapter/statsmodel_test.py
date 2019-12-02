from tests.utils import GIVEN, WHEN, THEN
from app.third_party_adapter.statsmodel import WeightedLinearRegression
from numpy import isnan, nan


def test_model():
    GIVEN("a set of co-ordinate data and some weights")
    y = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert round(model.get("alpha"), 6) == 1
    assert round(model.get("Beta"), 6) == 1.1

    GIVEN("a set of co-ordinate data and some weights")
    y = [0, 0, 0, 0, 0, 0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert round(model.get("alpha"), 6) == 0
    assert round(model.get("Beta"), 6) == 0


    GIVEN("a set of co-ordinate data and some weights")
    y = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [1, 1, 1, 1, 1, 1]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert isnan(model.get("alpha"))
    assert isnan(model.get("Beta"))

    GIVEN("a set of co-ordinate data and some weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 9999999.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, nan]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert round(model.get("alpha"), 6) == 1
    assert round(model.get("Beta"), 6) == 1

    GIVEN("a set of co-ordinate data and some weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, nan]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert round(model.get("alpha"), 6) == 1
    assert round(model.get("Beta"), 6) == 1

    GIVEN("a set of co-ordinate data and some weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [nan, nan, nan, 2, 2, nan]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert isnan(model.get("alpha"))
    assert isnan(model.get("Beta"))

    GIVEN("a set of co-ordinate data and some weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [0, 0, 0, 2, 2, nan]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert isnan(model.get("alpha"))
    assert isnan(model.get("Beta"))

    GIVEN("a set of co-ordinate data and some weights")
    y = [1.0, nan, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, nan, 3.0, 4.0, 5.0]
    weights = [0, 2, 2, nan, 2, 2]
    WHEN("we instantiate the model class")
    model = WeightedLinearRegression(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert isnan(model.get("alpha"))
    assert isnan(model.get("Beta"))
