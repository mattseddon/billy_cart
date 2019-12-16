class OrdersHandler:
    def __init__(self, bank=5000):
        self.__bank = bank
        self.__existing_orders = []
        # needs
        # bank
        # id
        # offered_price,
        # probability

    def get_new_orders(self, wps):
        # calculate risk_percentage
        # split
        wps = [
            item
            for item in wps
            if item.get("risk_percentage") > 0
            and item.get("min_size") / self.__bank < item.get("risk_percentage")
            and item.get("id") not in self.get_existing_order_ids()
        ]

        bp = {}
        if wps:
            for item in wps:
                bp[item.get("id")] = item.get("risk_percentage")
                for item1 in wps:
                    if item.get("id") != item1.get("id"):
                        bp[item.get("id")] = bp[item.get("risk_percentage")] * (
                            1 - item1.get("risk_percentage")
                        )
                #apply existing percentages

        for item in wps:
            item["risk_percentage"] = bp[item.get("id")]
            item["order_size"] = round(
                max(min(item.get("risk_percentage"), 0.05) * self.__bank, 5), 2
            )

        wps = [item for item in wps if item["bet_size"] > 0]

        self.__existing_orders.extend(wps)

        return wps

    def get_existing_order_probabilities(self):
        pass

    def get_existing_order_ids(self):
        return [order.get("id") for order in self.__existing_orders]

    def _get_existing_order_risk_percentages(self):
        pass

    def _calc_total_return(self, price):
        return self.__calc_return(price) + 1

    # this will need to go into the business rules
    def __calc_return(self, price):
        return (price - 1) * (1 - self.__calc_comission_percentage())

    def __calc_comission_percentage(self, discount_rate=0):
        return 0.05 * (1 - discount_rate)

    def __calc_risk_percentage(self, probability, price, kf=1, cap=0.05):
        risk_return = self.__calc_return(price)
        if (probability * price) - 1 > 0:
            risk_percentage = min(
                max(
                    ((risk_return * probability) ** kf - (1 - probability) ** kf)
                    / (
                        (risk_return * probability) ** kf
                        + risk_return * (1 - probability) ** kf
                    ),
                    0,
                ),
                cap,
            )
        else:
            risk_percentage = 0
        return risk_percentage
