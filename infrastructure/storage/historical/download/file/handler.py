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

        self.__calls = 0
        if mediator:
            Colleague.__init__(self, mediator=mediator)

        self._file_data = super().get_file_as_list()
        self._market_definition = self._get_market_definition()
        self._data = HistoricalDownloadFileDataHandler(
            items=self._get_items_definition(),
            market_start_time=self.get_market_start_time(),
        )
        market = list(
            filter(
                lambda record: record,
                map(lambda record: self._data.process(record), self._file_data),
            )
        )
        self._market = self._gap_fill(market=market)

    def get_market_start_time(self):
        return self._market_definition.get("marketTime")

    def get_file_as_list(self):
        return self._market

    def _gap_fill(self, market):
        m = []
        for index, record in enumerate(market):
            if index > 0:
                previous_record = market[index - 1]
                m.extend(
                    self.__make_extra_records(
                        frm=previous_record,
                        time_diff=(
                            record.get("extract_time")
                            - (previous_record.get("extract_time"))
                        ),
                    )
                )
            m.append(record)
        return m

    def __make_extra_records(self, frm, time_diff):
        extra_records = []
        for seconds in range(1, time_diff):
            record = make_copy(frm)
            record["extract_time"] += seconds
            extra_records.append(record)
        return extra_records

    def _get_market_definition(self):
        return self._file_data[0].get("mc")[0].get("marketDefinition")

    def _get_items_definition(self):
        return self._market_definition.get("runners")

    def get_market(self):
        data = self._market[self.__calls]
        self.__calls = self.__calls + 1
        print(self.__calls)

        return self._mediator.notify(event="external data fetched", data=data)

    def get_outcome(self):
        return next(
            map(
                lambda item: item.get("id"),
                filter(
                    lambda item: item.get("status") == "WINNER",
                    self._file_data[-1]
                    .get("mc")[0]
                    .get("marketDefinition")
                    .get("runners"),
                ),
            )
        )

    def post_order(self, orders):

        print(orders)

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
