from tests.utils import GIVEN, WHEN, THEN, lists_are_equal

from infrastructure.third_party.adapter.numpy_utils import (
    is_not_a_number,
    not_a_number,
    not_a_number_to_number,
)
from infrastructure.third_party.adapter.data_container import DataContainer


def test_new():
    GIVEN("a data container")
    data_container = DataContainer()
    WHEN("we call new")
    new_container = data_container.new()
    THEN("a data container is returned")
    assert type(new_container) is type(data_container)
    THEN("the new data container is a different instance")
    assert new_container is not data_container


def test_add_rows():
    GIVEN("two data containers containing simple data")
    data = __get_test_dict()
    data_container = DataContainer(data)
    data_to_add = {"B": [12], "A": [6], "D": ["extra column"]}
    data_container_to_add = DataContainer(data_to_add)
    WHEN("we add the first to the second")
    data_container.add_rows(data_container_to_add)
    THEN("we have the correct number of rows and columns")
    unique_keys = set().union(data.keys(), data_to_add.keys())
    assert data_container.get_row_count() == max(
        [
            len(data.get(key) or []) + len(data_to_add.get(key) or [])
            for key in unique_keys
        ]
    )
    assert data_container.get_column_count() == len(unique_keys)


def test_set_index():
    GIVEN("a simple set of data and a container")
    data = __get_test_dict()
    data_container = DataContainer(data)
    WHEN("we set the index to be A")
    data_container.set_index(columns=["A"])
    assert data_container.get_column_count() == len(data.keys()) - 1
    assert lists_are_equal(data_container.get_index(), data.get("A"))

    GIVEN("a simple set of data and a container")
    data = __get_test_dict()
    data_container = DataContainer(data)
    WHEN("we set the index to be A and B")
    data_container.set_index(columns=["A", "B"])
    assert data_container.get_column_count() == len(data.keys()) - 2
    assert lists_are_equal(
        data_container.get_index(),
        [(data.get("A")[row], data.get("B")[row]) for row in range(len(data.get("B")))],
    )


def test_column_group_name():
    GIVEN(
        "some data that contains ids in the keys and"
        + " a container with the column group's name of the ids to be id"
    )
    data = {
        ("col1", 123): [1, 2, 3, 4],
        ("col1", 456): [1, 2, 3, 4],
        ("col2", 123): [1, 2, 3, 4],
        ("col2", 456): [1, 2, 3, 4],
    }
    data_container = DataContainer(data)
    data_container.set_column_group_name(name="id", level=1)
    WHEN("we get the column names from the id group")
    ids = data_container.get_column_group_values(name="id")
    THEN("the correct ids are returned")
    assert lists_are_equal(ids, [123, 456])

    GIVEN(
        "some data that contains ids in the keys and a"
        + " container with the column group's name of the ids to be id"
    )
    data = {
        ("col1", 123): [1, 2, 3, 4],
        ("col1", 456): [1, 2, 3, 4],
        ("col2", 123): [1, 2, 3, 4],
        ("col2", 456): [1, 2, 3, 4],
    }
    data_container = DataContainer(data)
    data_container.set_column_group_name(names=["variable", "id"])
    WHEN("we get the column names from the id group")
    ids = data_container.get_column_group_values(name="id")
    THEN("the correct ids are returned")
    assert lists_are_equal(ids, [123, 456])
    WHEN("we get the column names from the variable group")
    variables = data_container.get_column_group_values(name="variable")
    THEN("the correct variables are returned")
    assert lists_are_equal(variables, ["col1", "col2"])

    GIVEN("some simple data and a container with the column name set to vars")
    data = {"col1": [1, 2, 3, 4], "col2": [1, 2, 3, 4]}
    data_container = DataContainer(data)
    data_container.set_column_group_name(name="vars")
    WHEN("we get the columns from the id group ")
    columns = data_container.get_column_group_values(name="vars")
    THEN("the correct columns are returned")
    assert lists_are_equal(columns, ["col1", "col2"])


def test_sum_columns():
    GIVEN("a simple set of data and a container")
    data = __get_test_dict()
    data_container = DataContainer(data)
    WHEN("we sum columns A and B to give D")
    data_container.sum_columns(output="D", columns=["A", "C"])
    THEN("the resulting data is correct")
    col_d = data_container.get_column(name="D")
    for row in range(len(data.get("C"))):
        assert col_d[row] == not_a_number_to_number(
            data.get("A")[row]
        ) + not_a_number_to_number(data.get("C")[row])


def test_get_last_column_entry():
    GIVEN("a simple set of data and a container")
    data = __get_test_dict()
    data_container = DataContainer(data)

    WHEN("we get the last entry for A")
    last_a = data_container.get_last_column_entry("A")
    THEN("the correct value is returned")
    assert last_a == data.get("A")[-1]
    assert isinstance(last_a, float)

    WHEN("we get the last entry for B")
    last_b = data_container.get_last_column_entry("B")
    THEN("the correct value is returned")
    assert last_b == data.get("B")[-1]
    assert isinstance(last_b, str)

    WHEN("we get the last entry for C")
    last_c = data_container.get_last_column_entry("C")
    THEN("the correct value is returned")
    assert is_not_a_number(last_c)


def test_has_column():
    GIVEN("a simple set of data and a container")
    data = __get_test_dict()
    data_container = DataContainer(data)

    WHEN("we check if the container has the column A")
    true = data_container.has_column("A")
    THEN("it does")
    assert true

    WHEN("we check if the container has the column wwwwweeeeeeeeeeeee")
    true = data_container.has_column("wwwwweeeeeeeeeeeee")
    THEN("it does not")
    assert not true

    GIVEN("an empty container")
    data_container = DataContainer()

    WHEN("we check if the container has the column ('closed_indicator','')")
    true = data_container.has_column(("closed_indicator", ""))
    THEN("it does not")
    assert not true


def __get_test_dict():
    return {
        "A": [1, 2, 3, 4, 5.000000],
        "B": [7, 8, 9, 10, "11.1234"],
        "C": [13, 15, 16, 17, not_a_number()],
    }
