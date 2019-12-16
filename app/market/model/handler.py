from infrastructure.third_party.adapter.numpy_utils import calculate_log, not_a_number
from infrastructure.built_in.adapter.copy_utils import make_copy


class ModelHandler:
    def __init__(self, wls_model, event_country="AU"):
        self.__event_country = event_country
        self.wls_model = wls_model

    def get_results(self, items):

        self.__market_back_size = self.__get_market_back_size(items=items)

        results = []
        for item in items:
            if (
                self._meets_wlr_criteria(item=item)
                and self._meets_wlr_threshold(item=item)
                and self._has_overlay(
                    item=item, probability="compositional_sp_probability"
                )
            ):
                has_value = self.__standardise_result(
                    item=item,
                    probability="compositional_sp_probability",
                    type="BUY",
                    model_id="SPMB",
                    buy_price="ex_offered_back_price",
                )
                results.append(has_value)
                continue

            elif (
                self._meets_high_back_size_threshold(item=item)
                and self.__event_country == "AU"
                and self._has_overlay(
                    item=item, probability="compositional_ex_probability"
                )
            ):
                has_value = self.__standardise_result(
                    item=item,
                    probability="compositional_ex_probability",
                    type="BUY",
                    model_id="MBG2",
                    buy_price="ex_offered_back_price",
                )
                results.append(has_value)
                continue

            elif (
                self._meets_low_back_size_threshold(item=item)
                and self.__event_country == "AU"
                and self._has_overlay(
                    item=item, probability="compositional_ex_probability"
                )
            ):
                has_value = self.__standardise_result(
                    item=item,
                    probability="compositional_ex_probability",
                    type="BUY",
                    model_id="MBL2",
                    buy_price="ex_offered_back_price",
                )
                results.append(has_value)
                continue

        return results

    def __standardise_result(self, item, probability, type, model_id, buy_price):
        has_value = {}
        has_value["id"] = item.get("id")
        has_value["probability"] = item.get(probability)
        has_value["type"] = type
        has_value["model_id"] = model_id
        has_value["buy_price"] = item.get(buy_price)
        return has_value

    def _has_overlay(self, item, probability):
        return item.get(probability) > (1 / item.get("ex_offered_back_price"))

    def _meets_wlr_criteria(self, item):

        y = self._get_log_returns(y=item.get("compositional_sp_back_price_ts"))

        self.wls_model.run(
            y=y,
            x=item.get("extract_time_ts"),
            weights=item.get("combined_back_size_ts"),
        )

        alpha = self.wls_model.get_alpha()
        Beta = self.wls_model.get_Beta()

        return Beta < 0 and alpha < -0.00001

    def _meets_wlr_threshold(self, item):
        back_size = item.get("combined_back_size")
        return (
            back_size >= 5000 and self.__event_country != "GB"
        ) or back_size >= 30000

    def _meets_high_back_size_threshold(self, item):
        back_size = item.get("combined_back_size")
        return (
            item.get("ex_offered_back_price") > 2
            and (back_size / self.__market_back_size) >= 0.6
            and back_size >= 20000
        )

    def _meets_low_back_size_threshold(self, item):
        back_size = item.get("combined_back_size")
        offered_back_price = item.get("ex_offered_back_price")
        return (
            offered_back_price <= 2
            and (back_size / self.__market_back_size)
            >= max([0.6, (1 / offered_back_price)])
            and back_size >= 10000
        )

    def _get_log_returns(self, y):
        list = make_copy(y)
        shifted_lift = make_copy(list)
        shifted_lift.pop()
        shifted_lift.insert(0, not_a_number())
        return [
            calculate_log(point_in_time / previous_point_in_time)
            for point_in_time, previous_point_in_time in zip(list, shifted_lift)
        ]

    def __get_market_back_size(self, items):
        market_back_size = 0
        for item in items:
            market_back_size += item.get("combined_back_size")
        return market_back_size

