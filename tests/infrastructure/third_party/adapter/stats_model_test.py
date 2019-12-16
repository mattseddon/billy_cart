from tests.utils import GIVEN, WHEN, THEN, almost_equal
from infrastructure.third_party.adapter.stats_model import WeightedLinearRegression
from infrastructure.third_party.adapter.numpy_utils import is_not_a_number, not_a_number


def test_weighted_linear_regression():
    GIVEN("a valid set of co-ordinate data and some weights")
    y = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert almost_equal(model.get_alpha(), 1)
    assert almost_equal(model.get_Beta(), 1.1)

    GIVEN("another valid set of co-ordinate data and some weights")
    y = [0, 0, 0, 0, 0, 0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert almost_equal(model.get_alpha(), 0)
    assert almost_equal(model.get_Beta(), 0)


def test_non_uniform_lists():
    GIVEN("a set of data with differing lengths")
    y = [0, 0, 0, 0, 0, 0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("the input data is rejected and NaNs are returned")
    assert is_not_a_number(model.get_alpha())
    assert is_not_a_number(model.get_Beta())


def test_zero_weights():
    GIVEN("a set of co-ordinate data and only invalid weights")
    y = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [1, 1, 1, 1, 1, 1]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("there are not enough valid records and NaNs are returned")
    assert is_not_a_number(model.get_alpha())
    assert is_not_a_number(model.get_Beta())


def test_single_invalid_record():
    GIVEN("a set of co-ordinate data (with one invalid record) and some weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 9999999.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, not_a_number()]
    weights = [2, 2, 2, 2, 2, 2]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert almost_equal(model.get_alpha(), 1)
    assert almost_equal(model.get_Beta(), 1)

    GIVEN("a set of co-ordinate data and some weights (one of which being invalid)")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [2, 2, 2, 2, 2, not_a_number()]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("the correct alpha and beta parameters are returned")
    assert almost_equal(model.get_alpha(), 1)
    assert almost_equal(model.get_Beta(), 1)


def test_less_than_3_valid():
    GIVEN("a set of co-ordinate data and only two valid weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [not_a_number(), not_a_number(), not_a_number(), 2, 2, not_a_number()]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("there are not enough valid records and NaNs are returned")
    assert is_not_a_number(model.get_alpha())
    assert is_not_a_number(model.get_Beta())

    GIVEN("a set of co-ordinate data and only two valid weights")
    y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    weights = [0, 0, 0, 2, 2, not_a_number()]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("there are not enough valid records and NaNs are returned")
    assert is_not_a_number(model.get_alpha())
    assert is_not_a_number(model.get_Beta())

    GIVEN("only two valid records")
    y = [1.0, not_a_number(), 3.0, 4.0, 5.0, 6.0]
    x = [0.0, 1.0, not_a_number(), 3.0, 4.0, 5.0]
    weights = [0, 2, 2, not_a_number(), 2, 2]
    WHEN("we instantiate the class and run the model")
    model = WeightedLinearRegression()
    model.run(y=y, x=x, weights=weights)
    THEN("there are not enough valid records and NaNs are returned")
    assert is_not_a_number(model.get_alpha())
    assert is_not_a_number(model.get_Beta())
