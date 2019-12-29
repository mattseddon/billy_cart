from app.colleague import Colleague


class OrdersHandler(Colleague):
    def __init__(self, mediator, bank=5000):
        self.__bank = bank
        self.__existing_orders = []
        Colleague.__init__(self, mediator=mediator)

    def prevent_reorder(self, orders):
        valid_orders = list(filter(lambda order: self.__is_valid_order(order), orders))
        self.__existing_orders.extend(valid_orders)
        return None

    def _get_existing_orders(self):
        return self.__existing_orders

    def get_new_orders(self, items):

        if not (items):
            return self.__notify_mediator_finished()

        risk_percentage = list(
            filter(
                lambda item: self.__is_valid_risk(item=item),
                map(lambda item: self.__add_data(item=item), items),
            )
        )

        self.__reduced_risk_percentage = self._calc_reduced_risk_percentage(
            initial_risk_percentage=risk_percentage
        )

        orders = list(
            filter(
                lambda order: self.__is_valid_order(order),
                (map(lambda item: self.__prepare_order(item), risk_percentage,)),
            )
        )

        return (
            self._mediator.notify(event="new orders", data=orders)
            if orders
            else self.__notify_mediator_finished()
        )

    def get_successful_orders(self, response, orders):

        successful_order_ids = self.__get_successful_order_ids(response=response)
        successful_orders = self.__filter_orders(
            orders=orders, successful_ids=successful_order_ids
        )

        return successful_orders

    def __get_successful_order_ids(self, response):
        return list(
            map(
                lambda order: order.get("instruction").get("selectionId"),
                filter(lambda order: self.__get_successful_order(order), response),
            )
        )

    def __get_successful_order(self, order):
        return order.get("status") == "SUCCESS"

    def __filter_orders(self, orders, successful_ids):
        return list(
            filter(lambda order: int(order.get("id")) in successful_ids, orders)
        )

    def __is_valid_order(self, order):
        return (
            order.get("size")
            and order.get("min_size")
            and order.get("size") > order.get("min_size") > 0
            and order.get("id")
            and order.get("probability")
            and 0 < order.get("probability") < 1
            and order.get("type") in ["BUY", "SELL"]
            and order.get("ex_price")
            and order.get("ex_price") > 0
            and self.__is_valid_risk(order)
        )

    def __add_data(self, item):
        item_with_risk = self.__add_risk_percentage(item)
        complete_item = self.__add_min_size(item_with_risk)
        return complete_item

    def __add_risk_percentage(self, item):
        item["risk_percentage"] = self._calc_risk_percentage(
            probability=item.get("probability"), price=item.get("returns_price")
        )
        return item

    def __add_min_size(self, item):
        item["min_size"] = 5
        return item

    def __is_valid_risk(self, item):
        return (
            item.get("risk_percentage")
            and item.get("risk_percentage") > 0
            and item.get("min_size") / self.__bank < item.get("risk_percentage")
            and item.get("id") not in self.get_existing_order_ids()
        )

    def _calc_reduced_risk_percentage(self, initial_risk_percentage):

        reduced_risk_percentage = {
            item.get("id"): item.get("risk_percentage")
            for item in initial_risk_percentage
        }

        risk_percentage = (
            initial_risk_percentage + self._get_existing_order_risk_percentages()
        )

        if len(initial_risk_percentage) > 1:
            for id in reduced_risk_percentage.keys():
                for another_item in risk_percentage:
                    if id != another_item.get("id"):
                        reduced_risk_percentage[id] *= 1 - (
                            another_item.get("risk_percentage") or 0
                        )
        return reduced_risk_percentage

    def __prepare_order(self, item):

        item["risk_percentage"] = self.__reduced_risk_percentage[item.get("id")]
        item["size"] = self._calc_order_size(item=item)
        return item

    def get_existing_order_probabilities(self):
        pass

    def get_existing_order_ids(self):
        return [order.get("id") for order in self._get_existing_orders()]

    def _get_existing_order_risk_percentages(self):
        return []

    def _calc_risk_percentage(self, probability, price, kf=1, cap=0.05):
        if self.__can_calculate_risk(probability=probability, price=price):
            risk_percentage = min(
                max(
                    ((price * probability) ** kf - (1 - probability) ** kf)
                    / ((price * probability) ** kf + (price * (1 - probability)) ** kf),
                    0,
                ),
                cap,
            )
        else:
            risk_percentage = 0
        return risk_percentage

    def __can_calculate_risk(self, probability, price):
        return (probability * price) - 1 > 0 and price > 0 and probability > 0

    def _calc_order_size(self, item):
        non_negative_risk_percentage = max(item.get("risk_percentage"), 0)
        monetary_size = round(non_negative_risk_percentage * self.__bank, 2)
        return monetary_size

    def __notify_mediator_finished(self):
        return self._mediator.notify(event="finished processing", data=None)

