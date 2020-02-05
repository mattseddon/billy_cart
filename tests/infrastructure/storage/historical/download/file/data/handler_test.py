from tests.utils import GIVEN, WHEN, THEN
from infrastructure.storage.historical.download.file.handler import (
    HistoricalDownloadFileDataHandler,
)
from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.built_in.adapter.copy_utils import make_copy


def test_handler():
    GIVEN("that we have a list of items and the market time")
    market_start_time = "2019-09-30T20:42:00.000Z"
    items = __get_default_items()
    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileDataHandler(
        items=items, market_start_time=market_start_time
    )
    THEN("the market_start_time matches the handler's market_start_time")
    assert handler._market_start_time == DateTime(market_start_time).get_epoch()

    THEN("the handler has a dictionary of items")
    assert type(handler._items) is dict
    THEN("there are the same number of keys in the dictionary as there are items")
    assert len(handler._items.keys()) > 0
    assert len(handler._items.keys()) == len(items)
    THEN("the handler's items have the correct ids")
    assert list(handler._items.keys()) == __get_from_list("id", items)
    THEN("the handler has a closed indicator")
    assert handler._closed_indicator == False


def test_process():
    GIVEN("a set of records and an handler")

    first_record = {"pt": -301 * 1000, "mc": [{"rc": []}]}

    second_record = __get_test_spn_record()
    second_record["pt"] = -300 * 1000

    third_record = __get_test_spb_record()
    third_record["pt"] = -(300 * 1000) + 1

    fourth_record = __get_test_ex_record()
    fourth_record["pt"] = (10 * 1000) + 5

    fifth_record = {"pt": (10 * 1000) + 6, "mc": [{"rc": []}]}

    items = __get_default_items()
    handler = HistoricalDownloadFileDataHandler(
        items=items, market_start_time="1970-01-01T00:00:00.000Z"
    )

    WHEN("we process the first record")
    first_dict = handler.process(first_record)

    THEN(
        "the extract time is outside of the required range and so an empty dict is return"
    )
    assert first_dict == {}
    THEN("the handler's items have not changed")
    assert handler._items == __get_default_dict()

    WHEN("we process the second record")
    second_dict = handler.process(second_record)

    THEN(
        "the extract time is inside of the required range and so a dict with the extract time is return"
    )
    expected_dict = {}
    expected_dict["items"] = __get_default_dict()
    expected_dict["extract_time"] = -300
    expected_dict["closed_indicator"] = False
    assert second_dict == expected_dict

    THEN("the extract time has been added to the handler's list of seen times")
    existing_times = [-300]
    assert handler._existing_times == existing_times

    THEN("the handler's items have changed")
    second_items = __add_all(__get_default_dict(), second_record)
    assert handler._items == second_items

    THEN(
        "the handler's items differ from the returned dict as the change happened after the extract time"
    )
    assert handler._items != second_dict.get("items")

    WHEN("we process the third record")
    third_dict = handler.process(third_record)

    THEN("the extract time has already been seen so an empty dict is return")
    assert third_dict == {}

    THEN("the handler's items have been updated")
    third_items = __add_all(second_items, third_record)
    assert handler._items == third_items
    assert handler._items != second_items

    WHEN("we process the fourth record")
    fourth_dict = handler.process(fourth_record)

    THEN(
        "the extract time is inside of the required range and so a dict with the extract time is return"
    )
    expected_dict = {}
    expected_dict["items"] = third_items
    expected_dict["extract_time"] = 10
    expected_dict["closed_indicator"] = False
    assert fourth_dict == expected_dict

    THEN("the extract time has been added to the handler's list of seen times")
    existing_times.append(10)
    assert handler._existing_times == existing_times

    THEN("the handler's items have been updated")
    fourth_items = __add_all(third_items, fourth_record)
    assert handler._items == fourth_items
    assert handler._items != third_items

    THEN(
        "the handler's items differ from the returned dict as the change happened after the extract time"
    )
    assert handler._items != fourth_dict.get("items")

    WHEN("we process the fifth record")
    fifth_dict = handler.process(fifth_record)

    THEN("the extract time has already been seen so an empty dict is return")
    assert fifth_dict == {}
    THEN("the extract times remain unchanged")
    assert handler._existing_times == existing_times
    THEN("the handler's items have not changed")
    assert handler._items == fourth_items


def test_ex_record():
    GIVEN("a set of default items and a data record")

    record = __get_test_ex_record()
    items = __get_default_items()

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileDataHandler(
        items=items, market_start_time="2020-01-01T00:00:00.000Z"
    )
    handler.set_record(record=record)
    default_dict = __get_default_dict()

    THEN("the handler contains the correct items")
    assert handler._items == default_dict

    WHEN("we add the available to back")
    handler._add_available_to_back()

    THEN("the correct items exist in the object")
    dict_atb = __add_atb(default_dict)
    assert handler._items == dict_atb

    WHEN("we add the available to lay data")
    handler._add_available_to_lay()

    THEN("the correct items exist in the object")
    dict_atb_atl = __add_atl(dict_atb)
    assert handler._items == dict_atb_atl

    WHEN("we add the traded volume data")
    handler._add_traded_volume()

    THEN("the correct items exist in the object")
    assert handler._items == __add_trd(dict_atb_atl)

    GIVEN("another instantiated handler")
    another_handler = HistoricalDownloadFileDataHandler(
        items=__get_default_items(), market_start_time="2020-01-01T00:00:00.000Z"
    )
    WHEN("we add all of the exchange data")
    another_handler.set_record(record=record)
    another_handler._add_exchange_data()
    THEN("the correct items exist in the new handler")
    assert another_handler._items == handler._items


def test_sp_records():
    GIVEN("some default items and a set of sp data records")

    items = __get_default_items()
    spb_record = __get_test_spb_record()
    spl_record = __get_test_spl_record()
    spn_record = __get_test_spn_record()

    WHEN("we instantiate the handler")
    handler = HistoricalDownloadFileDataHandler(
        items=items, market_start_time="2020-01-01T00:00:00.000Z"
    )

    THEN("the handler has the correct default items")
    default_dict = __get_default_dict()
    assert handler._items == default_dict

    WHEN("we add the sp back taken")
    handler.set_record(record=spb_record)
    handler._add_sp_back_taken()
    THEN("the correct items exist within the handler")
    dict_spb = __add_spb(default_dict)
    assert handler._items == dict_spb

    WHEN("we add the sp lay taken")
    handler.set_record(record=spl_record)
    handler._add_sp_lay_taken()
    THEN("the correct items exist within the handler")
    dict_spb_spl = __add_spl(dict_spb)
    assert handler._items == dict_spb_spl

    WHEN("we add the sp near price")
    handler.set_record(record=spn_record)
    handler._add_sp_near_price()
    THEN("the correct items exist within the handler")
    dict_sp = __add_spn(dict_spb_spl)
    assert handler._items == __add_spn(dict_sp)


def test_removal_date():
    GIVEN("a handler and a record with no removal date for any of the items")
    market_start_time = "2019-08-03T06:05:00.000Z"
    removal_date_str = "2019-08-01T04:20:12.000Z"
    items_definition = __get_items_with_late_removal()
    handler = HistoricalDownloadFileDataHandler(
        items=items_definition, market_start_time=market_start_time
    )

    WHEN("we get the items")
    items = handler._items

    THEN("none of the items have a removal date")
    expected = __get_default_dict(items=items_definition)
    assert items == expected

    WHEN("we add some data with no removal date")
    non_removal_data = __get_non_removed_data()
    handler.process(non_removal_data)

    THEN("the items are as expected")
    expected = __add_all(expected, non_removal_data)
    assert handler._items == expected

    THEN("the item which is going to be removed has some data")
    assert handler._items.get(23304992) != {
        **__get_default_ex_dict(),
        **__get_default_sp_dict(),
    }

    WHEN("we add some data that shows an items has been removed")
    removal_data = __get_removed_data()
    handler.process(removal_data)

    THEN("the items are as expected")
    expected = __add_all(expected, removal_data)
    expected[23304992]["removal_date"] = removal_date_str
    assert handler._items == expected

    THEN("the correct items has a removal date")
    removal_date = handler._items.get(23304992).get("removal_date")
    assert type(removal_date) is str
    THEN("the removal date can be converted to an epoch")
    removal_epoch = DateTime(removal_date).get_epoch()
    assert removal_epoch > 0
    THEN("the epoch is before the start time")
    assert removal_epoch < DateTime(market_start_time).get_epoch()
    THEN("the removal date is before the process time")
    assert removal_epoch < DateTime(removal_data.get("pt")).get_epoch()

    WHEN("we add some more data that has no mention of items being removed")
    post_removal_data = __get_post_removed_data()
    handler.process(post_removal_data)

    THEN("the items are as expected")
    expected = __add_all(expected, post_removal_data)
    assert handler._items == expected

    THEN("the removed item's data has been reset")
    assert handler._items.get(23304992) == {
        **__get_default_ex_dict(),
        **__get_default_sp_dict(),
        "removal_date": removal_date_str,
    }


def test_closed_indicator():
    GIVEN("a handler and a set of records to process")

    first_record = {"pt": -301 * 1000, "mc": [{"rc": []}]}
    second_record = __get_test_spn_record()
    second_record["pt"] = -300 * 1000
    third_record = __get_test_spb_record()
    third_record["pt"] = -(300 * 1000) + 1
    fourth_record = __get_test_ex_record()
    fourth_record["pt"] = (10 * 1000) + 5
    fifth_record = __get_test_closed_record()

    items = __get_default_items()
    handler = HistoricalDownloadFileDataHandler(
        items=items, market_start_time="1970-01-01T00:00:00.000Z"
    )

    WHEN("we process the first four record")
    handler.process(first_record)
    handler.process(second_record)
    handler.process(third_record)
    handler.process(fourth_record)

    expected = __add_all(__get_default_dict(), second_record)
    expected = __add_all(expected, third_record)
    expected = __add_all(expected, fourth_record)

    THEN("the handler's items are as expected")
    assert handler._items == expected

    THEN("the market's closed indicator is set to False")
    assert handler._closed_indicator == False

    WHEN("we process the first fifth record")
    handler.process(fifth_record)

    THEN("the handler's items have not changed")
    assert handler._items == expected

    THEN("the market's closed indicator is set to True")
    assert handler._closed_indicator == True


def test_get_item_changes():
    GIVEN("an handler and a data record")

    handler = HistoricalDownloadFileDataHandler(
        items=__get_default_items(), market_start_time="2020-01-01T00:00:00.000Z"
    )
    record = __get_test_ex_record()
    handler.set_record(record=record)

    WHEN("we get the item changes")
    items = handler._get_item_changes()
    THEN("the correct items are returned")
    assert items == [
        {"atb": [[7.4, 6.46]], "id": 21145599},
        {"atb": [[8.4, 3.29]], "id": 26291825},
        {"atl": [[8.4, 0]], "id": 26291825},
        {"trd": [[8.4, 20.97]], "ltp": 8.4, "tv": 20.97, "id": 26291825},
        {"atb": [[2, 0], [2.02, 0]], "id": 19795432},
        {"atl": [[2, 3.33], [2.08, 14.35]], "id": 19795432},
        {
            "trd": [[2, 230.89], [2.02, 971.32], [2.06, 653.45]],
            "ltp": 2.0,
            "tv": 1855.66,
            "id": 19795432,
        },
    ]


def __get_default_dict(items=None):
    ids = __get_ids_from_items_definition(items)
    return {id: {**__get_default_ex_dict(), **__get_default_sp_dict()} for id in ids}


def __get_default_ex_dict():
    return {"ex": {"atb": {}, "atl": {}, "trd": {}}}


def __get_default_sp_dict():
    return {"sp": {"spn": None, "spb": {}, "spl": {}}}


def __get_test_ex_record():
    return {
        "op": "mcm",
        "clk": "10208996912",
        "pt": 1569876388371,
        "mc": [
            {
                "id": "1.163093692",
                "rc": [
                    {"atb": [[7.4, 6.46]], "id": 21145599},
                    {"atb": [[8.4, 3.29]], "id": 26291825},
                    {"atl": [[8.4, 0]], "id": 26291825},
                    {"trd": [[8.4, 20.97]], "ltp": 8.4, "tv": 20.97, "id": 26291825},
                    {"atb": [[2, 0], [2.02, 0]], "id": 19795432},
                    {"atl": [[2, 3.33], [2.08, 14.35]], "id": 19795432},
                    {
                        "trd": [[2, 230.89], [2.02, 971.32], [2.06, 653.45]],
                        "ltp": 2.0,
                        "tv": 1855.66,
                        "id": 19795432,
                    },
                ],
            }
        ],
    }


def __get_test_spb_record():
    return {
        "op": "mcm",
        "clk": "10208999228",
        "pt": 1569876445713,
        "mc": [
            {
                "id": "1.163093692",
                "rc": [
                    {"spb": [[1000, 195.26]], "id": 21145599},
                    {"atb": [[1.4, 3.11], [8.8, 0]], "id": 26291825},
                    {"spb": [[1000, 293.38]], "id": 26291825},
                    {"trd": [[8.8, 8.14]], "ltp": 8.8, "tv": 8.14, "id": 26291825},
                    {"spb": [[1000, 508.78]], "id": 26291824},
                    {"spb": [[1000, 68.14]], "id": 19795432},
                    {"spb": [[1000, 213.5]], "id": 26291827},
                    {"spb": [[1000, 435.84]], "id": 25197628},
                    {"spb": [[1000, 183.87]], "id": 26291826},
                    {"atl": [[13, 0.05]], "id": 26291826},
                    {"spb": [[1000, 236]], "id": 418},
                ],
            }
        ],
    }


def __get_test_spl_record():
    return {
        "op": "mcm",
        "clk": "10208999639",
        "pt": 1569876455939,
        "mc": [
            {
                "id": "1.163093692",
                "rc": [
                    {"atb": [[8.6, 2]], "id": 21145599},
                    {"spl": [[1.01, 58.03]], "id": 26291825},
                    {"atb": [[8.6, 2.55]], "id": 26291825},
                    {"trd": [[8.6, 7]], "ltp": 8.6, "tv": 7.0, "id": 26291825},
                    {"spl": [[1.01, 13.56]], "id": 26291824},
                    {"atb": [[1.78, 2.57], [1.79, 0]], "id": 19795432},
                    {
                        "trd": [[1.78, 52.85], [1.79, 32.33]],
                        "ltp": 1.78,
                        "tv": 85.18,
                        "id": 19795432,
                    },
                    {"spl": [[1.01, 10]], "id": 26291827},
                    {"spl": [[1.01, 14]], "id": 25197628},
                    {"spl": [[1.01, 62]], "id": 26291826},
                    {"spl": [[1.01, 21]], "id": 418},
                ],
            }
        ],
    }


def __get_test_spn_record():
    return {
        "op": "mcm",
        "clk": "10209001405",
        "pt": 1569876502566,
        "mc": [
            {
                "id": "1.163093692",
                "rc": [
                    {"spn": 9.48, "spf": 9.48, "id": 21145599},
                    {"spn": 8.8, "spf": 8.27, "id": 26291825},
                    {"spn": 55.0, "spf": 41.61, "id": 26291824},
                    {"spn": 1.76, "spf": 1.61, "id": 19795432},
                    {"spn": 107.7, "spf": 107.7, "id": 26291827},
                    {"spn": 39.46, "spf": 39.0, "id": 25197628},
                    {"atb": [[8.2, 0]], "id": 26291826},
                    {"atl": [[8.2, 38.01]], "id": 26291826},
                    {"trd": [[8.2, 114.8]], "ltp": 8.2, "tv": 114.8, "id": 26291826},
                    {"spn": 8.0, "spf": 7.86, "id": 26291826},
                    {"spn": 14.0, "spf": 13.5, "id": 418},
                ],
            }
        ],
    }


def __get_test_closed_record():
    true = True
    false = False
    return {
        "op": "mcm",
        "clk": "10209001692",
        "pt": 1569876511866,
        "mc": [
            {
                "id": "1.163093692",
                "marketDefinition": {
                    "bspMarket": true,
                    "turnInPlayEnabled": true,
                    "persistenceEnabled": true,
                    "marketBaseRate": 5.0,
                    "eventId": "29502644",
                    "eventTypeId": "7",
                    "numberOfWinners": 1,
                    "bettingType": "ODDS",
                    "marketType": "WIN",
                    "marketTime": "2019-09-30T20:42:00.000Z",
                    "suspendTime": "2019-09-30T20:42:00.000Z",
                    "bspReconciled": true,
                    "complete": true,
                    "inPlay": true,
                    "crossMatching": true,
                    "runnersVoidable": false,
                    "numberOfActiveRunners": 8,
                    "betDelay": 1,
                    "status": "OPEN",
                    "runners": [
                        {
                            "adjustmentFactor": 6.09,
                            "status": "ACTIVE",
                            "sortPriority": 1,
                            "bsp": 9.18,
                            "id": 26291825,
                            "name": "Shangjia",
                        },
                        {
                            "adjustmentFactor": 49.56,
                            "status": "ACTIVE",
                            "sortPriority": 2,
                            "bsp": 1.82,
                            "id": 19795432,
                            "name": "Shes My Gem",
                        },
                        {
                            "adjustmentFactor": 3.79,
                            "status": "ACTIVE",
                            "sortPriority": 3,
                            "bsp": 16.09,
                            "id": 418,
                            "name": "Inglenook",
                        },
                        {
                            "adjustmentFactor": 3.48,
                            "status": "ACTIVE",
                            "sortPriority": 4,
                            "bsp": 73.1,
                            "id": 26291824,
                            "name": "Sebastianna",
                        },
                        {
                            "adjustmentFactor": 2.77,
                            "status": "ACTIVE",
                            "sortPriority": 5,
                            "bsp": 132.42,
                            "id": 26291827,
                            "name": "Bluesberry Gal",
                        },
                        {
                            "adjustmentFactor": 3.37,
                            "status": "ACTIVE",
                            "sortPriority": 6,
                            "bsp": 48.0,
                            "id": 25197628,
                            "name": "Combine Road",
                        },
                        {
                            "adjustmentFactor": 7.14,
                            "status": "ACTIVE",
                            "sortPriority": 7,
                            "bsp": 9.6,
                            "id": 21145599,
                            "name": "Singing Hills",
                        },
                        {
                            "adjustmentFactor": 23.76,
                            "status": "ACTIVE",
                            "sortPriority": 8,
                            "bsp": 8.2,
                            "id": 26291826,
                            "name": "Miss Kitty Mae",
                        },
                    ],
                    "regulators": ["MR_NJ", "MR_INT"],
                    "venue": "Zia Park",
                    "countryCode": "US",
                    "discountAllowed": true,
                    "timezone": "US/Mountain",
                    "openDate": "2019-09-30T18:00:00.000Z",
                    "version": 2968936820,
                    "name": "R7 6f Mdn",
                    "eventName": "ZiaP (US) 30th Sep",
                },
                "rc": [],
                "con": true,
                "img": false,
            }
        ],
    }


def __add_all(d, record):
    dict = make_copy(d)
    dict = __add_atb(dict, record)
    dict = __add_atl(dict, record)
    dict = __add_trd(dict, record)
    dict = __add_spb(dict, record)
    dict = __add_spl(dict, record)
    dict = __add_spn(dict, record)
    return dict


def __add_atb(d, record=__get_test_ex_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("atb"):
            for price in change.get("atb"):
                if price[1]:
                    dict[change.get("id")]["ex"]["atb"][price[0]] = price[1]
                elif price[1] == 0 and dict[change.get("id")]["ex"]["atb"].get(
                    price[0]
                ):
                    del dict[change.get("id")]["ex"]["atb"][price[0]]
    return dict


def __add_atl(d, record=__get_test_ex_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("atl"):
            for price in change.get("atl"):
                if price[1]:
                    dict[change.get("id")]["ex"]["atl"][price[0]] = price[1]
                elif price[1] == 0 and dict[change.get("id")]["ex"]["atl"].get(
                    price[0]
                ):
                    del dict[change.get("id")]["ex"]["atl"][price[0]]
    return dict


def __add_trd(d, record=__get_test_ex_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("trd"):
            for price in change.get("trd"):
                if price[1]:
                    dict[change.get("id")]["ex"]["trd"][price[0]] = price[1]
                elif price[1] == 0 and dict[change.get("id")]["ex"]["trd"].get(
                    price[0]
                ):
                    del dict[change.get("id")]["ex"]["trd"][price[0]]
    return dict


def __add_spb(d, record=__get_test_spb_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("spb"):
            dict[change.get("id")]["sp"]["spb"][change.get("spb")[0][0]] = change.get(
                "spb"
            )[0][1]
    return dict


def __add_spl(d, record=__get_test_spl_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("spl"):
            dict[change.get("id")]["sp"]["spl"][change.get("spl")[0][0]] = change.get(
                "spl"
            )[0][1]
    return dict


def __add_spn(d, record=__get_test_spn_record()):
    dict = make_copy(d)
    for change in __get_rc(record):
        if change.get("spn"):
            dict[change.get("id")]["sp"]["spn"] = change.get("spn")
    return dict


def __get_default_items():
    return [
        {
            "adjustmentFactor": 15.27,
            "status": "ACTIVE",
            "sortPriority": 1,
            "id": 26291825,
            "name": "Shangjia",
        },
        {
            "adjustmentFactor": 44.43,
            "status": "ACTIVE",
            "sortPriority": 2,
            "id": 19795432,
            "name": "Shes My Gem",
        },
        {
            "adjustmentFactor": 9.83,
            "status": "ACTIVE",
            "sortPriority": 3,
            "id": 418,
            "name": "Inglenook",
        },
        {
            "adjustmentFactor": 4.99,
            "status": "ACTIVE",
            "sortPriority": 4,
            "id": 26291824,
            "name": "Sebastianna",
        },
        {
            "adjustmentFactor": 2.61,
            "status": "ACTIVE",
            "sortPriority": 5,
            "id": 26291827,
            "name": "Bluesberry Gal",
        },
        {
            "adjustmentFactor": 4.48,
            "status": "ACTIVE",
            "sortPriority": 6,
            "id": 25197628,
            "name": "Combine Road",
        },
        {
            "adjustmentFactor": 12.36,
            "status": "ACTIVE",
            "sortPriority": 7,
            "id": 21145599,
            "name": "Singing Hills",
        },
        {
            "adjustmentFactor": 6.0,
            "status": "ACTIVE",
            "sortPriority": 8,
            "id": 26291826,
            "name": "Miss Kitty Mae",
        },
    ]


def __get_items_with_late_removal():
    return [
        {
            "adjustmentFactor": 4.13,
            "status": "ACTIVE",
            "sortPriority": 1,
            "id": 14381554,
            "name": "1. Hogmanay",
        },
        {
            "adjustmentFactor": 5.66,
            "status": "ACTIVE",
            "sortPriority": 2,
            "id": 17286447,
            "name": "2. Primitivo",
        },
        {
            "adjustmentFactor": 21.96,
            "status": "ACTIVE",
            "sortPriority": 3,
            "id": 19648211,
            "name": "3. Monsieur Sisu",
        },
        {
            "adjustmentFactor": 3.2,
            "status": "ACTIVE",
            "sortPriority": 4,
            "id": 23304992,
            "name": "4. Our Gravano",
        },
        {
            "adjustmentFactor": 5.28,
            "status": "ACTIVE",
            "sortPriority": 5,
            "id": 9279305,
            "name": "5. Pirate Ben",
        },
        {
            "adjustmentFactor": 12.07,
            "status": "ACTIVE",
            "sortPriority": 6,
            "id": 5358796,
            "name": "6. Costello",
        },
        {
            "adjustmentFactor": 13.9,
            "status": "ACTIVE",
            "sortPriority": 7,
            "id": 25279656,
            "name": "7. Cyber Intervention",
        },
        {
            "adjustmentFactor": 1.8,
            "status": "ACTIVE",
            "sortPriority": 8,
            "id": 814252,
            "name": "8. The Bandit",
        },
        {
            "adjustmentFactor": 11.32,
            "status": "ACTIVE",
            "sortPriority": 9,
            "id": 21318216,
            "name": "9. Exasperate",
        },
        {
            "adjustmentFactor": 10.65,
            "status": "ACTIVE",
            "sortPriority": 10,
            "id": 21150150,
            "name": "10. Ulusaba",
        },
        {
            "adjustmentFactor": 1.8,
            "status": "ACTIVE",
            "sortPriority": 11,
            "id": 17203692,
            "name": "11. Island Missile",
        },
        {
            "adjustmentFactor": 7.14,
            "status": "ACTIVE",
            "sortPriority": 12,
            "id": 24405589,
            "name": "12. Matowi",
        },
        {
            "adjustmentFactor": 1.05,
            "status": "ACTIVE",
            "sortPriority": 13,
            "id": 25279657,
            "name": "13. On Angels Wings",
        },
    ]


def __get_non_removed_data():
    return {
        "op": "mcm",
        "clk": "9757207096",
        "pt": 1564631269663,
        "mc": [
            {
                "id": "1.160904847",
                "rc": [
                    {"atb": [[1.17, 85.47]], "id": 19648211},
                    {"atb": [[1.17, 85.47]], "id": 17286447},
                    {"atb": [[1.17, 85.47]], "id": 25279656},
                    {"atb": [[1.17, 85.47]], "id": 25279657},
                    {"atb": [[1.17, 85.47]], "id": 23304992},
                    {"atb": [[1.17, 85.47]], "id": 21150150},
                    {"atb": [[1.17, 85.47]], "id": 5358796},
                    {"atb": [[1.17, 85.47]], "id": 24405589},
                    {"atb": [[1.17, 85.47]], "id": 814252},
                    {"atb": [[1.17, 85.47]], "id": 17203692},
                    {"atb": [[1.17, 85.47]], "id": 21318216},
                    {"atb": [[1.17, 85.47]], "id": 9279305},
                    {"atb": [[1.17, 85.47]], "id": 14381554},
                ],
            }
        ],
    }


def __get_removed_data():
    true = True
    false = False
    return {
        "op": "mcm",
        "clk": "9757281567",
        "pt": 1564633213343,
        "mc": [
            {
                "id": "1.160904847",
                "marketDefinition": {
                    "bspMarket": true,
                    "turnInPlayEnabled": true,
                    "persistenceEnabled": true,
                    "marketBaseRate": 10.0,
                    "eventId": "29392310",
                    "eventTypeId": "7",
                    "numberOfWinners": 1,
                    "bettingType": "ODDS",
                    "marketType": "WIN",
                    "marketTime": "2019-08-03T06:05:00.000Z",
                    "suspendTime": "2019-08-03T06:05:00.000Z",
                    "bspReconciled": false,
                    "complete": true,
                    "inPlay": false,
                    "crossMatching": false,
                    "runnersVoidable": false,
                    "numberOfActiveRunners": 13,
                    "betDelay": 0,
                    "status": "SUSPENDED",
                    "runners": [
                        {
                            "adjustmentFactor": 4.34,
                            "status": "ACTIVE",
                            "sortPriority": 1,
                            "id": 14381554,
                            "name": "1. Hogmanay",
                        },
                        {
                            "adjustmentFactor": 11.06,
                            "status": "ACTIVE",
                            "sortPriority": 2,
                            "id": 17286447,
                            "name": "2. Primitivo",
                        },
                        {
                            "adjustmentFactor": 4.54,
                            "status": "ACTIVE",
                            "sortPriority": 3,
                            "id": 19648211,
                            "name": "3. Monsieur Sisu",
                        },
                        {
                            "adjustmentFactor": 4.54,
                            "status": "ACTIVE",
                            "sortPriority": 4,
                            "removalDate": "2019-08-01T04:20:12.000Z",
                            "id": 23304992,
                            "name": "4. Our Gravano",
                        },
                        {
                            "adjustmentFactor": 2.38,
                            "status": "ACTIVE",
                            "sortPriority": 5,
                            "id": 9279305,
                            "name": "5. Pirate Ben",
                        },
                        {
                            "adjustmentFactor": 14.28,
                            "status": "ACTIVE",
                            "sortPriority": 6,
                            "id": 5358796,
                            "name": "6. Costello",
                        },
                        {
                            "adjustmentFactor": 24.39,
                            "status": "ACTIVE",
                            "sortPriority": 7,
                            "id": 25279656,
                            "name": "7. Cyber Intervention",
                        },
                        {
                            "adjustmentFactor": 1.17,
                            "status": "ACTIVE",
                            "sortPriority": 8,
                            "id": 814252,
                            "name": "8. The Bandit",
                        },
                        {
                            "adjustmentFactor": 11.11,
                            "status": "ACTIVE",
                            "sortPriority": 9,
                            "id": 21318216,
                            "name": "9. Exasperate",
                        },
                        {
                            "adjustmentFactor": 9.09,
                            "status": "ACTIVE",
                            "sortPriority": 10,
                            "id": 21150150,
                            "name": "10. Ulusaba",
                        },
                        {
                            "adjustmentFactor": 2.56,
                            "status": "ACTIVE",
                            "sortPriority": 11,
                            "id": 17203692,
                            "name": "11. Island Missile",
                        },
                        {
                            "adjustmentFactor": 9.09,
                            "status": "ACTIVE",
                            "sortPriority": 12,
                            "id": 24405589,
                            "name": "12. Matowi",
                        },
                        {
                            "adjustmentFactor": 1.4,
                            "status": "ACTIVE",
                            "sortPriority": 13,
                            "id": 25279657,
                            "name": "13. On Angels Wings",
                        },
                    ],
                    "regulators": ["MR_NJ", "MR_INT"],
                    "venue": "Randwick",
                    "countryCode": "AU",
                    "discountAllowed": true,
                    "timezone": "Australia/Sydney",
                    "openDate": "2019-08-03T01:45:00.000Z",
                    "version": 2875565714,
                    "name": "R8 1800m Hcap",
                    "eventName": "Rand (AUS) 3rd Aug",
                },
                "rc": [],
            }
        ],
    }


def __get_post_removed_data():
    return {
        "op": "mcm",
        "clk": "9757281567",
        "pt": 1564633213343,
        "mc": [
            {
                "id": "1.160904847",
                "rc": [
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 19648211,
                    },
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 17286447,
                    },
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 25279656,
                    },
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 25279657,
                    },
                    {
                        "atb": [
                            [1.01, 0],
                            [1.03, 0],
                            [1.11, 0],
                            [1.02, 0],
                            [1.13, 0],
                            [1.1, 0],
                            [1.17, 0],
                        ],
                        "id": 23304992,
                    },
                    {"atl": [[690, 0], [55, 0], [980, 0]], "id": 23304992},
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 21150150,
                    },
                    {"atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]], "id": 5358796},
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 24405589,
                    },
                    {"atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]], "id": 814252},
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 17203692,
                    },
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 21318216,
                    },
                    {"atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]], "id": 9279305},
                    {
                        "atb": [[1.11, 0], [1.13, 0], [1.1, 0], [1.17, 0]],
                        "id": 14381554,
                    },
                ],
            }
        ],
    }


def __get_rc(dict):
    return dict["mc"][0].get("rc")


def __get_ids_from_items_definition(items=None):
    return [item.get("id") for item in items or __get_default_items()]


def __get_from_list(name, l):
    return list(map(lambda item: item.get(name), l))
