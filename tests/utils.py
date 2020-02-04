from infrastructure.built_in.adapter.os_utils import (
    get_file_path,
    make_directory_if_required,
    remove_directory,
    remove_file,
)


def GIVEN(str):
    print("\nGIVEN {}".format(str))


def WHEN(str):
    print("    WHEN {}".format(str))


def THEN(str):
    print("        THEN {}".format(str))
    pass


def get_test_directory():
    return "./test_data"


def get_test_file_path(name):
    directory = __make_test_directory()
    file_path = get_file_path(directory=directory, file=name) if directory else None
    return file_path


def lists_are_equal(first, second):
    return len(first) == len(second) and sorted(first) == sorted(second)


def almost_equal(first, second):
    return abs((first) - (second)) < 0.0000001


def __make_test_directory():
    directory = get_test_directory()
    path = make_directory_if_required(directory)
    return path


def cleanup_test_file(name):
    directory = get_test_directory()
    path = get_file_path(directory=directory, file=name)
    file_exists = remove_file(path=path)
    directory_exists = cleanup_test_directory()
    return True if not (directory_exists or file_exists) else False


def cleanup_test_directory():
    directory = get_test_directory()
    directory_exists = remove_directory(directory)
    return True if not directory_exists else False


def get_test_orders():
    return [
        {"id": 9999999, "type": "BUY", "size": 100, "ex_price": 2.0},
        {"id": 8888888, "type": "SELL", "size": 6.18, "ex_price": 75.0},
        {"id": 7777777, "type": "BUY", "size": 5, "ex_price": 12.6},
    ]


def get_test_orders_post_response():
    return {
        "status": "SUCCESS",
        "instructionReports": [
            {
                "status": "SUCCESS",
                "sizeMatched": 100,
                "betId": "177444942426",
                "instruction": {
                    "handicap": 0.0,
                    "orderType": "LIMIT",
                    "selectionId": 9999999,
                    "limitOrder": {
                        "price": 2.0,
                        "persistenceType": "LAPSE",
                        "size": 100,
                    },
                    "side": "BACK",
                },
                "orderStatus": "EXECUTION_COMPLETE",
                "placedDate": "2019-09-05T06:26:30.000Z",
                "averagePriceMatched": 2,
            },
            {
                "status": "SUCCESS",
                "sizeMatched": 6.18,
                "betId": "177444942426",
                "instruction": {
                    "handicap": 0.0,
                    "orderType": "LIMIT",
                    "selectionId": 8888888,
                    "limitOrder": {
                        "price": 75.0,
                        "persistenceType": "LAPSE",
                        "size": 6.18,
                    },
                    "side": "LAY",
                },
                "orderStatus": "EXECUTION_COMPLETE",
                "placedDate": "2019-09-05T06:26:30.000Z",
                "averagePriceMatched": 75.0,
            },
            {
                "status": "SUCCESS",
                "sizeMatched": 5,
                "betId": "177444942426",
                "instruction": {
                    "handicap": 0.0,
                    "orderType": "LIMIT",
                    "selectionId": 7777777,
                    "limitOrder": {
                        "price": 12.6,
                        "persistenceType": "LAPSE",
                        "size": 5,
                    },
                    "side": "BACK",
                },
                "orderStatus": "EXECUTION_COMPLETE",
                "placedDate": "2019-09-05T06:26:30.000Z",
                "averagePriceMatched": 12.8,
            },
        ],
        "marketId": "123456",
    }

