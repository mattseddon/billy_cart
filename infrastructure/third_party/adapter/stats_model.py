from statsmodels.api import WLS, add_constant

from app.market.model.interface import WeightedLinearRegressionInterface

from infrastructure.third_party.adapter.numpy_utils import (
    calculate_log,
    not_a_number,
    is_not_a_number,
)


class WeightedLinearRegression(WeightedLinearRegressionInterface):
    def __init__(self):
        self.__y = None
        self.__x = None
        self.__weights = None
        self.__alpha = None
        self.__Beta = None
        self.__data = None

    def run(self, y, x, weights):
        self.__y = y
        self.__x = x
        self.__weights = self.__calc_log_weights(weights=weights)
        self.__alpha = not_a_number()
        self.__Beta = not_a_number()
        if self.__inputs_lengths_are_valid():
            valid_records = self.__calc_valid_records()
            if valid_records >= 3:
                self.__run_model()
        self.__data = {"alpha": self.__alpha, "Beta": self.__Beta}

    def get_alpha(self):
        return self.__data.get("alpha")

    def get_Beta(self):
        return self.__data.get("Beta")

    def __run_model(self):

        X = add_constant(self.__x)

        mod_wls = WLS(
            self.__y, X, weights=self.__weights, missing="drop", hasconst=True
        )
        res_wls = mod_wls.fit()
        self.__alpha = res_wls.params[1]
        self.__Beta = res_wls.params[0]

    def __calc_log_weights(self, weights):
        return [calculate_log(max(weight, 1)) for weight in weights]

    def __inputs_lengths_are_valid(self):
        return len(self.__y) == len(self.__x) and len(self.__y) == len(self.__weights)

    def __calc_valid_records(self):
        valid_records = 0
        for i, item in enumerate(self.__weights):
            if (
                not is_not_a_number(item)
                and item > 0
                and not is_not_a_number(self.__x[i])
                and not is_not_a_number(self.__y[i])
            ):
                valid_records += 1
        return valid_records
