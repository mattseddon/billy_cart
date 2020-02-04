from tests.utils import GIVEN, WHEN, THEN
from infrastructure.storage.historical.download.file.record.adapter import (
    HistoricalDownloadFileRecordAdapter,
)
from infrastructure.storage.historical.download.file.handler import (
    HistoricalDownloadFileHandler,
)
from infrastructure.third_party.adapter.numpy_utils import is_not_a_number
from pytest import mark


@mark.slow
def test_adapter():
    GIVEN("a file loaded in to the historical download file class and a record adapter")
    adapter = HistoricalDownloadFileRecordAdapter()
    directory = "./dev"
    file = "1.160904847.bz2"
    handler = HistoricalDownloadFileHandler(file=file, directory=directory)

    WHEN("we convert the records one at a time")
    for index, record in enumerate(handler.get_file_as_list()):
        data = adapter.convert(record)

        THEN("then a dict is returned")
        assert type(data) is dict

        THEN("for the first 300 records there is no closed indicator")
        if index < 300:
            assert not (data.get("closed_indicator"))

        THEN("the dict has an extract time which is an integer")
        extract_time = data.get("extract_time")
        assert type(extract_time) is int

        THEN("the dict has a list of items")
        items = data.get("items")
        assert type(items) is list

        THEN("each of the items is a dict")
        for item in items:
            assert type(item) is dict

        THEN("each of the items has the correct values for each attribute")
        for item in items:
            assert item.get("id")
            test_item = record.get("items").get(item.get("id"))

            if item.get("id") not in [23304992, 5358796, 17203692]:
                assert item.get("removal_date") is None
            else:
                assert item.get("removal_date")

            assert item.get("sp_back_size") == __calc_sp_back_size(test_item)

            ex_back_size = __calc_ex_back_size(test_item)
            assert item.get("ex_back_size") == ex_back_size

            assert item.get("sp_back_price") == test_item.get("sp").get("spn")

            ex_avg_back_price = item.get("ex_average_back_price")
            if ex_back_size:
                assert ex_avg_back_price == __calc_ex_avg_back_price(test_item)
            else:
                assert is_not_a_number(ex_avg_back_price)

            ex_offered_back_price = item.get("ex_offered_back_price")
            if test_item.get("ex").get("atb"):
                assert ex_offered_back_price == __get_ex_offered_back_price(test_item)
            else:
                assert is_not_a_number(ex_offered_back_price)

            assert item.get("sp_lay_size") == __calc_sp_lay_size(test_item)

            ex_lay_size = __calc_ex_lay_size(test_item)
            assert item.get("ex_lay_size") == ex_lay_size

            assert item.get("sp_lay_price") == __calc_sp_lay_price(test_item)

            ex_average_lay_price = item.get("ex_average_lay_price")
            if ex_lay_size:
                assert ex_average_lay_price == __calc_ex_avg_lay_price(test_item)
            else:
                assert is_not_a_number(ex_average_lay_price)

            available_to_lay = item.get("ex_offered_lay_price")
            test_available_to_lay = test_item.get("ex").get("atl")
            if test_available_to_lay:
                assert available_to_lay == min(test_available_to_lay)
            else:
                assert is_not_a_number(available_to_lay)


def test_adapter_single_record():
    GIVEN("a record from a test file and an adapter")
    record = __get_test_record()
    adapter = HistoricalDownloadFileRecordAdapter()

    WHEN("we call convert")
    data = adapter.convert(record)

    THEN("then a dict is returned")
    assert type(data) is dict

    THEN("the dict has an extract time which is an integer < 0 (before market started)")
    extract_time = data.get("extract_time")
    assert type(extract_time) is int
    assert extract_time < 0

    THEN("the dict has a list of items")
    items = data.get("items")
    assert type(items) is list

    THEN("each of the items is a dict")
    for item in items:
        assert type(item) is dict

    THEN("each of the items has the correct values for each attribute")
    for item in items:
        assert item.get("id")
        test_item = record.get("items").get(item.get("id"))

        assert item.get("removal_date") is None

        assert item.get("sp_back_size") == __calc_sp_back_size(test_item)

        ex_back_size = __calc_ex_back_size(test_item)
        assert item.get("ex_back_size") == ex_back_size

        assert item.get("sp_back_price") == test_item.get("sp").get("spn")

        ex_avg_back_price = item.get("ex_average_back_price")
        if ex_back_size:
            assert ex_avg_back_price == __calc_ex_avg_back_price(test_item)
        else:
            assert is_not_a_number(ex_avg_back_price)

        assert item.get("ex_offered_back_price") == __get_ex_offered_back_price(
            test_item
        )

        assert item.get("sp_lay_size") == __calc_sp_lay_size(test_item)

        ex_lay_size = __calc_ex_lay_size(test_item)
        assert item.get("ex_lay_size") == ex_lay_size

        assert item.get("sp_lay_price") == __calc_sp_lay_price(test_item)

        ex_average_lay_price = item.get("ex_average_lay_price")
        if ex_lay_size:
            assert ex_average_lay_price == __calc_ex_avg_lay_price(test_item)
        else:
            assert is_not_a_number(ex_average_lay_price)

        assert item.get("ex_offered_lay_price") == min(test_item.get("ex").get("atl"))

    THEN("the data has a closed indicator which is set to False")
    assert data.get("closed_indicator") == False


def test_get_max_valid_price():
    GIVEN("a dictionary and an adapter")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = __get_test_dict()
    WHEN("we get the max price")
    max_price = adapter._get_max_valid_price(dict)
    THEN("the max price is as expected")
    assert max_price == 990


def test_get_max_no_valid_price():
    GIVEN("a dictionary and an adapter")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = {}
    WHEN("we get the max price")
    max_price = adapter._get_max_valid_price(dict)
    THEN("the max price is as expected")
    assert is_not_a_number(max_price)


def test_get_min_valid_price():
    GIVEN("a dictionary and an adapter")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = __get_test_dict()
    WHEN("we get the min price")
    min_price = adapter._get_min_valid_price(dict)
    THEN("the max price is as expected")
    assert min_price == 5.9


def test_get_min_no_valid_price():
    GIVEN("a dictionary and an adapter")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = {}
    WHEN("we get the min price")
    min_price = adapter._get_min_valid_price(dict)
    THEN("the max price is as expected")
    assert is_not_a_number(min_price)


def test_sum_valid_values():
    GIVEN("an adapter and a dict")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = {1.01: 20, 3: 11, 4: 9, "a": 400, "200": 200, 0: None, 40: 0, None: 900}
    WHEN("we sum the valid values")
    total = adapter._sum_valid_sizes(dict)
    THEN("the correct value is returned")
    assert total == 40

def test_sum_valid_values_gt_1():
    GIVEN("an adapter and a dict (the price of 1 will not be counted)")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = {3: 11, 4: 9, 1: 20, "a": 400, "200": 200, 0: None, 40: 0, None: 900}
    WHEN("we sum the valid values")
    total = adapter._sum_valid_sizes(dict)
    THEN("the correct value is returned")
    assert total == 20


def test_sum_no_valid_values():
    GIVEN("an adapter and a dict")
    adapter = HistoricalDownloadFileRecordAdapter()
    dict = {}
    WHEN("we sum the valid values")
    total = adapter._sum_valid_sizes(dict)
    THEN("the correct value is returned")
    assert total == 0


def __get_test_record():
    return {
        "closed_indicator": False,
        "extract_time": -300,
        "items": {
            26291825: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1062.75,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        1.6: 146.66,
                        1.43: 250,
                        2: 2,
                        1.96: 2,
                        2.1: 2,
                        2.08: 2,
                        1.99: 25,
                        1.92: 2,
                        1.81: 41,
                        1.88: 35,
                        1.9: 2,
                        1.86: 2,
                        2.16: 15,
                        1.83: 2,
                        2.04: 2,
                        2.12: 18,
                        1.94: 30,
                        2.06: 21,
                        1.97: 2,
                        3.65: 2.21,
                        3.9: 2.21,
                        4.4: 2.39,
                        4.7: 1.5,
                        4.6: 0.17,
                        1.07: 0.23,
                        2.36: 65.64,
                        4.9: 0.6,
                        4.8: 1.94,
                    },
                    "trd": {4.7: 0.01},
                    "atl": {
                        420: 0.17,
                        48: 0.01,
                        95: 0.01,
                        190: 0.01,
                        9.4: 4,
                        8.8: 2.39,
                        990: 1.67,
                        6.2: 32.93,
                        6: 2,
                        5.9: 12,
                    },
                },
                "sp": {"spn": 4.77, "spb": {}, "spl": {220: 1.77, 1.01: 3}},
            },
            19795432: {
                "ex": {
                    "atb": {
                        1.06: 61.2,
                        1.01: 1097.69,
                        1.13: 400,
                        1.02: 526.58,
                        1.03: 3386.29,
                        1.49: 165.88,
                        1.7: 11.62,
                        1.2: 15,
                        1.18: 18,
                        1.12: 2,
                        1.14: 2,
                        1.09: 2,
                        1.08: 2,
                        1.16: 2,
                        1.15: 21,
                        1.11: 25,
                        1.17: 2,
                        1.04: 2,
                        1.77: 4.01,
                        1.86: 0.49,
                        1.88: 2.96,
                        1.91: 200.6,
                        1.96: 12,
                        2.04: 10,
                        2.08: 0.08,
                        2.06: 0.08,
                        2.1: 12,
                        2.12: 11.57,
                    },
                    "trd": {
                        1.71: 3.72,
                        1.72: 3.98,
                        1.49: 27.42,
                        1.51: 4.43,
                        1.52: 4.43,
                        2.9: 0.01,
                        2.18: 0.17,
                        2.72: 0.01,
                        2.38: 0.01,
                        2.04: 18.31,
                        2.22: 1.98,
                        2.24: 1.98,
                        2.06: 1.98,
                        2.2: 7.67,
                        2.02: 6.71,
                        1.96: 8.54,
                        1.81: 2.45,
                        1.92: 1.62,
                        1.88: 11.02,
                        1.99: 5.35,
                        1.94: 4.1,
                        1.93: 1.2,
                        1.97: 5.31,
                        2: 2.2,
                        1.98: 54.88,
                        2.08: 3.91,
                        2.12: 66.6,
                        2.1: 0.17,
                        2.16: 17.48,
                    },
                    "atl": {
                        420: 0.17,
                        48: 0.01,
                        95: 0.01,
                        190: 0.01,
                        4.1: 8,
                        3.65: 34,
                        3.5: 2,
                        3.4: 25,
                        3.85: 2,
                        3.1: 2,
                        3.35: 2,
                        3.25: 2,
                        4.4: 2,
                        3.75: 2,
                        3.2: 21,
                        3.95: 35,
                        2.98: 15,
                        3.55: 2,
                        3.05: 18,
                        4.6: 41,
                        3.15: 2,
                        2.96: 26.58,
                        2.9: 1.69,
                        2.24: 0.6,
                        2.8: 10.66,
                        2.44: 11.04,
                        2.18: 2.17,
                        2.68: 8.13,
                        2.72: 8.13,
                        2.84: 8.13,
                        3: 5,
                        2.38: 20,
                        2.22: 2,
                        2.2: 14,
                        2.5: 24,
                        2.28: 17,
                        2.54: 2,
                        2.32: 2,
                        2.26: 2,
                        2.42: 2,
                        2.6: 2,
                        2.64: 28,
                        2.46: 2,
                        2.34: 2,
                    },
                },
                "sp": {"spn": 2.1, "spb": {}, "spl": {200: 1.77}},
            },
            418: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1061.11,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        2.44: 61.11,
                        1.43: 250,
                        4.4: 2,
                        5.4: 18,
                        4: 2,
                        3.45: 41,
                        4.5: 2,
                        5: 2,
                        3.7: 2,
                        5.2: 2,
                        4.2: 30,
                        4.7: 25,
                        4.8: 2,
                        5.3: 2,
                        3.8: 35,
                        3.55: 2,
                        5.6: 15,
                        5.1: 21,
                        3.9: 2,
                        8.2: 10,
                        4.1: 28.59,
                        8.6: 2.16,
                        7.8: 4.08,
                        8.8: 2.87,
                        9: 2.04,
                    },
                    "trd": {},
                    "atl": {
                        420: 0.17,
                        48: 0.02,
                        95: 0.01,
                        190: 0.01,
                        55: 6,
                        60: 2,
                        46: 5.34,
                    },
                },
                "sp": {"spn": 27.4, "spb": {}, "spl": {210: 1.77}},
            },
            26291824: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1062.77,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        2.36: 64.7,
                        1.43: 250,
                        12: 1,
                        12.5: 1,
                        14: 15,
                        13: 18.54,
                        9.2: 2,
                        7.2: 2,
                        6.2: 41,
                        8: 26.14,
                        10: 1,
                        11: 1,
                        11.5: 21,
                        8.4: 2,
                        9.4: 2,
                        7.6: 35,
                        9.8: 25,
                        8.8: 30,
                        6.6: 2,
                        15.5: 4.2,
                        7.8: 13.12,
                        16: 1.78,
                        20: 0.16,
                        21: 0.15,
                    },
                    "trd": {16: 2.1, 17: 1.15, 21: 0.1},
                    "atl": {
                        420: 0.17,
                        48: 0.01,
                        95: 4.01,
                        190: 0.01,
                        900: 0.03,
                        34: 0.56,
                        24: 0.29,
                        65: 2.5,
                        40: 0.09,
                        50: 0.67,
                        60: 1.73,
                    },
                },
                "sp": {"spn": 22.5, "spb": {}, "spl": {210: 1.77}},
            },
            26291827: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1061.11,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        5.8: 18.33,
                        5.9: 2,
                        1.43: 250,
                        11: 18,
                        12: 15,
                        6.4: 2,
                        9.2: 2,
                        9.6: 2,
                        7.2: 2,
                        8.6: 2,
                        5.7: 41,
                        8: 53.6,
                        9: 25,
                        10: 1,
                        10.5: 1,
                        6.8: 35,
                        8.4: 2,
                        7.6: 2,
                        9.8: 21,
                        13.5: 10,
                        17: 1.35,
                        8.8: 11.43,
                        18.5: 0.6,
                        18: 0.38,
                        14: 5.64,
                        17.5: 0.84,
                        14.5: 0.36,
                    },
                    "trd": {},
                    "atl": {
                        420: 0.17,
                        1000: 1.67,
                        48: 0.01,
                        95: 0.01,
                        190: 0.01,
                        900: 0.03,
                    },
                },
                "sp": {"spn": 33.25, "spb": {}, "spl": {220: 1.77}},
            },
            25197628: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1061.11,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        3.65: 33.2,
                        1.43: 250,
                        3.6: 2,
                        3.85: 35,
                        4.9: 2,
                        3.5: 41,
                        3.75: 2,
                        5.4: 2,
                        4.5: 2,
                        3.95: 2,
                        5.5: 18,
                        5.2: 21,
                        5.7: 15,
                        4.8: 25,
                        4.3: 30,
                        5.3: 2,
                        5.1: 2,
                        4.6: 2,
                        4.1: 2,
                        1.1: 0.16,
                        6.8: 15.41,
                        15.5: 1.48,
                        16: 1.62,
                        16.5: 0.6,
                        7: 3.83,
                        7.2: 1.56,
                    },
                    "trd": {},
                    "atl": {
                        420: 0.17,
                        1000: 1.67,
                        48: 0.01,
                        95: 0.01,
                        190: 0.01,
                        900: 0.04,
                    },
                },
                "sp": {"spn": 32.25, "spb": {}, "spl": {200: 1.77, 85: 2.74}},
            },
            21145599: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1062.74,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        2.22: 72.13,
                        1.43: 250,
                        3.6: 25,
                        3.85: 2,
                        3.35: 30,
                        3.25: 2,
                        3.5: 37.45,
                        3.75: 2,
                        3.45: 2,
                        2.88: 41,
                        3.95: 18,
                        3.8: 21,
                        2.98: 2,
                        3.05: 35,
                        2.92: 2,
                        4.1: 15,
                        3.15: 2,
                        3.9: 2,
                        3.65: 2,
                        5.3: 3.5,
                        6.2: 1.98,
                        7: 0.6,
                        6: 2,
                        5.4: 0.82,
                        6.4: 0.83,
                    },
                    "trd": {},
                    "atl": {
                        420: 0.17,
                        140: 0.02,
                        48: 1.01,
                        95: 0.01,
                        190: 0.01,
                        27: 5,
                        26: 1,
                        32: 5.47,
                        25: 11,
                        34: 13,
                        38: 1,
                        40: 1,
                        44: 14,
                        55: 1,
                        65: 15,
                        75: 1,
                        90: 1,
                        23: 10,
                        100: 16,
                        28: 12,
                        29: 1,
                        18.5: 1.07,
                        9.6: 0.83,
                        17.5: 9.84,
                        17: 1.71,
                        16.5: 3.54,
                    },
                },
                "sp": {"spn": 6.17, "spb": {}, "spl": {210: 1.77, 1.01: 3}},
            },
            26291826: {
                "ex": {
                    "atb": {
                        1.06: 31.2,
                        1.01: 1062.7,
                        1.13: 400,
                        1.02: 528.57,
                        1.03: 430,
                        2.54: 57.14,
                        1.43: 250,
                        4.9: 30,
                        5.9: 2,
                        5.4: 25,
                        4.5: 2,
                        6.2: 18,
                        5.5: 2,
                        6: 2,
                        5.2: 2,
                        5.7: 2,
                        4.7: 2,
                        4.3: 35,
                        5.8: 21,
                        3.8: 41,
                        5.1: 2,
                        4.1: 2,
                        3.9: 2,
                        7: 14.77,
                        15: 1.53,
                        15.5: 2.25,
                        12.5: 3.4,
                    },
                    "trd": {},
                    "atl": {
                        420: 0.17,
                        48: 0.01,
                        95: 0.01,
                        190: 0.01,
                        70: 4,
                        30: 5,
                        29: 0.13,
                        28: 0.69,
                        55: 2,
                        990: 1.75,
                        27: 3.71,
                    },
                },
                "sp": {"spn": 21.25, "spb": {}, "spl": {200: 1.77, 55: 2.74}},
            },
        },
    }


def __get_test_dict():
    return {
        420: 0.17,
        48: 0.01,
        95: 0.01,
        190: 0.01,
        9.4: 4,
        8.8: 2.39,
        990: 1.67,
        6.2: 32.93,
        6: 2,
        5.9: 12,
        -400: 2,
        "a": 200,
        None: 600,
    }


def __calc_sp_back_size(item):
    return sum(item.get("sp").get("spb").values())


def __calc_ex_back_size(item):
    return sum(item.get("ex").get("trd").values())


def __calc_ex_avg_back_price(item):
    return sum(
        [price * size for price, size in item.get("ex").get("trd").items()]
    ) / __calc_ex_back_size(item)


def __get_ex_offered_back_price(item):
    return max(item.get("ex").get("atb").keys())


def __calc_sp_lay_size(item):
    return sum(item.get("sp").get("spl").values())


def __calc_ex_lay_size(item):
    return sum(
        [
            liability * (price - 1)
            for price, liability in item.get("ex").get("trd").items()
        ]
    )


def __calc_sp_lay_price(item):
    return 1 / (1 - (1 / item.get("sp").get("spn")))


def __calc_ex_avg_lay_price(item):
    return sum(
        [
            (1 / (1 - (1 / price))) * (size * (price - 1))
            for price, size in item.get("ex").get("trd").items()
        ]
    ) / __calc_ex_lay_size(item)
