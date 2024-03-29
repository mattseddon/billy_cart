from app.colleague import Colleague
from app.market.interface import ExternalAPIMarketInterface
from infrastructure.external_api.handler import ExternalAPIHandler
from infrastructure.storage.file.handler import FileHandler
from infrastructure.storage.historical.download.file.data.handler import (
    HistoricalDownloadFileDataHandler,
)
from infrastructure.built_in.adapter.copy_utils import make_copy


class HistoricalDownloadFileHandler(
    FileHandler, ExternalAPIHandler, ExternalAPIMarketInterface, Colleague
):
    def __init__(self, directory, file, mediator=None):
        super().__init__(directory=directory, file=file)

        if mediator:
            Colleague.__init__(self, mediator=mediator)

        self._market_definition = self._get_market_definition()
        if self.is_correct_type() and self.__ids_match(file):
            self._file_data = super().get_file_as_generator()
            self._data = HistoricalDownloadFileDataHandler(
                items=self._get_items_definition(),
                market_start_time=self.get_market_start_time(),
            )
            market = filter(
                lambda record: record,
                map(self._data.process, self._file_data),
            )
            self._market = self._gap_fill(market=market)
        else:
            self._market = iter([])

    def is_correct_type(self):
        return self._market_definition.get("marketType") == "WIN"

    def get_market_start_time(self):
        return self._market_definition.get("marketTime")

    def get_file_as_list(self):
        market = list(self._market)
        self._market = iter(market)
        return market

    def _gap_fill(self, market):
        previous_record = None
        for record in market:
            if previous_record:
                if previous_record.get("closed_indicator") is True:
                    break
                for extra_record in self.__make_extra_records(
                    frm=previous_record,
                    time_diff=(
                        record.get("extract_time")
                        - (previous_record.get("extract_time"))
                    ),
                ):
                    yield extra_record
            yield record
            previous_record = record

    def __ids_match(self, file):
        market_id = self.__get_market_id()
        file_id = file[:-4]
        return market_id == file_id

    def __get_market_id(self):
        return super().get_first_record().get("mc")[0].get("id")

    def __make_extra_records(self, frm, time_diff):
        for seconds in range(1, time_diff):
            record = make_copy(frm)
            record["extract_time"] += seconds
            yield record

    def _get_market_definition(self):
        return super().get_first_record().get("mc")[0].get("marketDefinition")

    def _get_items_definition(self):
        return self._market_definition.get("runners")

    def get_market(self):
        try:
            data = next(self._market)
            return self._mediator.notify(event="external data fetched", data=data)
        except:
            return None

    def get_outcome(self):
        outcome = next(
            map(
                lambda item: item.get("id"),
                filter(
                    lambda item: item.get("status") == "WINNER",
                    list(self._file_data)[-1]
                    .get("mc")[0]
                    .get("marketDefinition")
                    .get("runners"),
                ),
            )
        )
        return outcome

    def post_order(self, orders):

        valid_orders = self._validate_orders(orders=orders)

        if valid_orders:
            response = list(
                map(
                    lambda order: {
                        "instruction": {"selectionId": order.get("id")},
                        "status": "SUCCESS",
                    },
                    valid_orders,
                )
            )

            return self._mediator.notify(
                data={"response": response, "orders": orders}, event="orders posted"
            )

        else:
            return self._mediator.notify(event="finished processing", data=None)

    def _validate_orders(self, orders):
        valid_orders = list(filter(lambda order: self.__is_valid(order=order), orders))
        return valid_orders

    def __is_valid(self, order):
        try:
            is_valid = (
                order.get("id") > 0
                and order.get("type") in ["BUY", "SELL"]
                and order.get("ex_price") > 0
                and order.get("size") > 0
            )
        except:
            is_valid = False
        return is_valid
