from tests.utils import GIVEN, WHEN, THEN, lists_are_equal
from infrastructure.built_in.adapter.copy_utils import make_copy


def test_make_copy():
    GIVEN("a list with random contents")
    random_list = [45, 21, 333, 564, 75, 66, 459, 4, 78, 0]
    WHEN("we make a copy")
    different_l = make_copy(random_list)
    THEN("the lists are equal")
    assert lists_are_equal(random_list, different_l)
    WHEN("we remove the last item from the list's copy")
    last_item = different_l.pop()
    THEN("the lists are no longer equal")
    assert not lists_are_equal(random_list, different_l)
    assert last_item == random_list[-1]
