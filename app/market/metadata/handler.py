class MetadataHandler:
    def get_extended_variable_list(self):
        return self.get_required_variables() + self.get_unrequired_variables()

    def get_required_variables(self):
        return ["id", "removal_date"] + self.get_back_sizes() + self.get_back_prices()

    def get_back_sizes(self):
        return [
            "sp_back_size",
            "ex_back_size",
        ]

    def get_back_prices(self):
        return [
            "sp_back_price",
            "ex_average_back_price",
            "ex_offered_back_price",
        ]

    def get_unrequired_variables(self):
        return self.get_lay_sizes() + self.get_lay_prices()

    def get_lay_sizes(self):
        return [
            "sp_lay_size",
            "ex_lay_size",
        ]

    def get_lay_prices(self):
        return [
            "sp_lay_price",
            "ex_average_lay_price",
            "ex_offered_lay_price",
        ]

    def get_point_in_time_model_variables(self):
        return [
            "combined_back_size",
            "compositional_sp_probability",
            "compositional_ex_average_probability",
            "ex_offered_back_price",
            "ex_offered_back_price" + self.get_minus_commission_suffix(),
        ]

    def get_index_name(self):
        return "extract_time"

    def get_time_series_model_variables(self):
        return ["compositional_sp_back_price", "combined_back_size"]

    def get_point_in_time_suffix(self):
        return "_pit"

    def get_time_series_suffix(self):
        return "_ts"

    def get_minus_commission_suffix(self):
        return "_mc"
