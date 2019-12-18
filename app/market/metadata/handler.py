class MetadataHandler:
    def __init__(self):
        None

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
