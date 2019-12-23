from tests.utils import GIVEN, WHEN, THEN
from app.market.handler import MarketHandler
from app.market.interface import ExternalAPIMarketInterface

from infrastructure.external_api.market.record.adapter import RecordAdapter
from infrastructure.storage.handler import FileHandler

from infrastructure.built_in.adapter.json_utils import make_dict

from pytest import raises, fail, mark
from unittest.mock import patch


def test_place_order():
    GIVEN("a set of orders and a market handler")
    orders = [
        {"id": 9999999, "ex_price": 2, "size": 100, "type": "BUY"},
        {"id": 8888888, "ex_price": 75, "size": 6.18, "type": "BUY"},
        {"id": 7777777, "ex_price": 12.6, "size": 5, "type": "BUY"},
    ]
    handler = MarketHandler(
        market_id=123456, external_api=MockExternalAPIMarketHandler()
    )
    WHEN("we place the orders")
    successful_orders = handler.place_orders(orders=orders)
    THEN("a list of IDs are returned")
    assert successful_orders == orders


@patch("app.market.handler.MarketHandler.get_data")
def test_exit_run_on_closed(mock_external_api):
    GIVEN("a handler")
    handler = MarketHandler(
        market_id=123456, external_api=MockExternalAPIMarketHandler()
    )
    mock_external_api.return_value = __get_valid_response_dict()
    WHEN("we call run but the market has closed")
    with raises(SystemExit) as system_exit:
        handler.run()
    THEN("the system will exit")
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 0


@patch("app.market.handler.MarketHandler.get_data")
def test_exit_run_on_no_data(mock_external_api):
    GIVEN("a handler")
    handler = MarketHandler(
        market_id=45678, external_api=MockExternalAPIMarketHandler()
    )
    mock_external_api.return_value = {}
    WHEN("we call run and no data is return from the api")
    for i in range(9):
        try:
            THEN(
                "the handler will run %s time%s without error"
                % (i + 1, "s" if i > 0 else "")
            )
            handler.run()
        except SystemExit:
            fail("Unexpected SystemExit")

    WHEN("we call run and no data is returned a 10th time")
    with raises(SystemExit) as system_exit:
        handler.run()
    THEN("the system will exit")
    assert system_exit.type == SystemExit
    assert system_exit.value.code == 0


@mark.slow
@patch("app.market.handler.MarketHandler.get_data")
@patch("app.market.handler.MarketHandler._fix_item_probability")
def test_system(mock_set_prob, mock_external_api):
    GIVEN("a market handler and the directory and file name of a test file")
    directory = "./data/29184567"
    market_id = 1.156230797
    file = "%s.txt" % market_id
    raw_data = FileHandler(directory=directory, file=file).get_file_as_list()

    WHEN("we run the market handler for each record of the file")

    handler = MarketHandler(
        market_id=market_id, external_api=MockExternalAPIMarketHandler()
    )
    for raw_record in raw_data:
        mock_external_api.return_value = raw_record
        handler.run()

    THEN("an order has been made")
    orders = handler.orders._get_existing_orders()
    assert orders != {}
    THEN("a single call to fix the probability of the items being ordered was made")
    assert mock_set_prob.call_count == 1

    THEN("the correct orders were passed to the method")
    args, kwargs = mock_set_prob.call_args
    assert args == ()
    assert kwargs.get("orders") == orders


class MockExternalAPIMarketHandler(ExternalAPIMarketInterface):
    def post_order(self, orders):
        orders = list(map(lambda order: self.__make_successful(order), orders))
        return orders

    def __make_successful(self, order):
        return {"status": "SUCCESS", "instruction": {"selectionId": order.get("id")}}

    def get_market(self):
        pass


def __get_valid_response_dict():
    return make_dict(
        '{"totalMatched": 364.453208, "marketName": "R1 1600m CL2", "marketInfo": [{"status": "OPEN", "isMarketDataDelayed": false, "numberOfRunners": 6, "complete": true, "bspReconciled": false, "runnersVoidable": false, "betDelay": 0, "marketId": "1.153523462", "crossMatching": true, "totalMatched": 11572.39, "version": 2590617656, "lastMatchTime": "2019-01-13T04:18:22.485Z", "numberOfWinners": 1, "inplay": true, "numberOfActiveRunners": 6, "totalAvailable": 244873.41, "runners": [{"status": "ACTIVE", "handicap": 0.0, "selectionId": 2320993, "sp": {"nearPrice": 4.292248027113674, "backStakeTaken": [{"price": 1.01, "size": 454.11}, {"price": 1.3, "size": 100.0}, {"price": 4.7, "size": 10.0}, {"price": 6.6, "size": 20.0}, {"price": 12.0, "size": 15.0}], "farPrice": 1.262463642, "layLiabilityTaken": [{"price": 1000.0, "size": 84.58}, {"price": 11.0, "size": 44.0}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 3254.5, "adjustmentFactor": 25.0, "ex": {"availableToBack": [{"price": 4.0, "size": 97.1}, {"price": 3.95, "size": 71.1}, {"price": 3.9, "size": 30.96}], "availableToLay": [{"price": 4.2, "size": 20.88}, {"price": 4.3, "size": 85.06}, {"price": 4.4, "size": 46.12}], "tradedVolume": [{"price": 3.25, "size": 32.92}, {"price": 3.3, "size": 7.08}, {"price": 3.85, "size": 19.74}, {"price": 3.95, "size": 36.33}, {"price": 4.0, "size": 450.48}, {"price": 4.1, "size": 383.67}, {"price": 4.2, "size": 339.86}, {"price": 4.3, "size": 256.44}, {"price": 4.4, "size": 366.97}, {"price": 4.5, "size": 894.81}, {"price": 4.6, "size": 22.21}, {"price": 4.8, "size": 10.0}, {"price": 5.0, "size": 434.0}]}, "lastPriceTraded": 4.1}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 21427613, "sp": {"nearPrice": 6.035664381750683, "backStakeTaken": [{"price": 1.01, "size": 100.0}, {"price": 9.0, "size": 20.0}], "farPrice": 1.74, "layLiabilityTaken": [{"price": 1000.0, "size": 62.05}, {"price": 11.0, "size": 44.0}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 2609.03, "adjustmentFactor": 14.085, "ex": {"availableToBack": [{"price": 7.0, "size": 39.63}, {"price": 6.8, "size": 83.63}, {"price": 6.6, "size": 156.86}], "availableToLay": [{"price": 7.2, "size": 51.99}, {"price": 7.4, "size": 22.88}, {"price": 7.6, "size": 18.16}], "tradedVolume": [{"price": 5.4, "size": 76.44}, {"price": 5.8, "size": 12.0}, {"price": 5.9, "size": 0.02}, {"price": 6.0, "size": 0.4}, {"price": 6.2, "size": 101.27}, {"price": 6.4, "size": 572.14}, {"price": 6.6, "size": 573.89}, {"price": 6.8, "size": 583.34}, {"price": 7.0, "size": 382.82}, {"price": 7.2, "size": 106.31}, {"price": 7.4, "size": 76.2}, {"price": 7.6, "size": 107.47}, {"price": 7.8, "size": 16.74}]}, "lastPriceTraded": 7.0}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 21059172, "sp": {"nearPrice": 3.5132056962946425, "backStakeTaken": [{"price": 1.01, "size": 210.18}], "farPrice": 1.51655879, "layLiabilityTaken": [{"price": 1000.0, "size": 23.15}, {"price": 11.0, "size": 44.0}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 1075.07, "adjustmentFactor": 28.911, "ex": {"availableToBack": [{"price": 3.65, "size": 119.8}, {"price": 3.6, "size": 595.21}, {"price": 3.55, "size": 170.47}], "availableToLay": [{"price": 3.7, "size": 28.36}, {"price": 3.75, "size": 32.71}, {"price": 3.8, "size": 39.8}], "tradedVolume": [{"price": 3.3, "size": 59.41}, {"price": 3.35, "size": 84.85}, {"price": 3.45, "size": 18.14}, {"price": 3.5, "size": 294.19}, {"price": 3.55, "size": 308.87}, {"price": 3.6, "size": 164.0}, {"price": 3.65, "size": 111.98}, {"price": 3.7, "size": 33.64}]}, "lastPriceTraded": 3.65}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 21662195, "sp": {"nearPrice": 5.509852539, "backStakeTaken": [{"price": 1.01, "size": 117.0}, {"price": 24.0, "size": 15.0}], "farPrice": 1.530120482, "layLiabilityTaken": [{"price": 1000.0, "size": 27.6}, {"price": 990.0, "size": 100.0}, {"price": 11.0, "size": 44.0}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 2639.26, "adjustmentFactor": 17.241, "ex": {"availableToBack": [{"price": 6.0, "size": 43.55}, {"price": 5.9, "size": 88.28}, {"price": 5.8, "size": 45.86}], "availableToLay": [{"price": 6.2, "size": 26.47}, {"price": 6.4, "size": 63.63}, {"price": 6.6, "size": 68.8}], "tradedVolume": [{"price": 4.7, "size": 70.0}, {"price": 5.4, "size": 0.75}, {"price": 5.5, "size": 19.84}, {"price": 5.6, "size": 809.05}, {"price": 5.7, "size": 707.38}, {"price": 5.8, "size": 197.76}, {"price": 5.9, "size": 217.39}, {"price": 6.0, "size": 497.37}, {"price": 6.2, "size": 119.73}]}, "lastPriceTraded": 6.0}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 22381578, "sp": {"nearPrice": 6.0, "backStakeTaken": [{"price": 1.01, "size": 65.0}, {"price": 6.6, "size": 20.0}, {"price": 14.5, "size": 15.0}], "farPrice": 3.990612903225806, "layLiabilityTaken": [{"price": 1000.0, "size": 92.71}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 1809.66, "adjustmentFactor": 11.628, "ex": {"availableToBack": [{"price": 5.8, "size": 72.78}, {"price": 5.7, "size": 108.21}, {"price": 5.6, "size": 113.49}], "availableToLay": [{"price": 5.9, "size": 44.4}, {"price": 6.0, "size": 112.02}, {"price": 6.2, "size": 50.49}], "tradedVolume": [{"price": 5.4, "size": 70.0}, {"price": 5.6, "size": 70.39}, {"price": 5.7, "size": 111.57}, {"price": 5.8, "size": 246.11}, {"price": 5.9, "size": 187.49}, {"price": 6.0, "size": 481.83}, {"price": 6.2, "size": 451.27}, {"price": 6.4, "size": 33.54}, {"price": 6.6, "size": 28.69}, {"price": 6.8, "size": 10.0}, {"price": 7.0, "size": 100.31}, {"price": 7.2, "size": 18.46}]}, "lastPriceTraded": 5.8}, {"status": "ACTIVE", "handicap": 0.0, "selectionId": 21949486, "sp": {"nearPrice": 88.37895780883844, "backStakeTaken": [{"price": 1.01, "size": 18.18}, {"price": 15.0, "size": 20.0}], "farPrice": 16.78793252652877, "layLiabilityTaken": [{"price": 1000.0, "size": 606.63}, {"price": 1.08, "size": 31.79}]}, "totalMatched": 184.85, "adjustmentFactor": 3.135, "ex": {"availableToBack": [{"price": 100.0, "size": 9.33}, {"price": 90.0, "size": 25.58}, {"price": 70.0, "size": 48.97}], "availableToLay": [{"price": 120.0, "size": 8.67}, {"price": 130.0, "size": 15.0}, {"price": 180.0, "size": 14.72}], "tradedVolume": [{"price": 95.0, "size": 20.54}, {"price": 100.0, "size": 27.07}, {"price": 110.0, "size": 10.44}, {"price": 120.0, "size": 27.55}, {"price": 130.0, "size": 66.89}, {"price": 140.0, "size": 17.9}, {"price": 150.0, "size": 7.96}, {"price": 180.0, "size": 6.36}, {"price": 190.0, "size": 0.16}]}, "lastPriceTraded": 120.0}]}], "marketStartTime": "2019-01-13T04:19:00.000Z", "et": "2019-01-13T04:19:00Z", "marketId": "1.153523462"}'
    )

