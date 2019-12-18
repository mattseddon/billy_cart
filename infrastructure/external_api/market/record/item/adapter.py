from infrastructure.built_in.adapter.date_time import DateTime
from infrastructure.third_party.adapter.numpy_utils import not_a_number
from infrastructure.external_api.market.record.interface import ItemAdapterInterface
from app.market.metadata.handler import MetadataHandler


class ItemAdapter(ItemAdapterInterface):
    def __init__(self, record, metadata=MetadataHandler()):
        self.__record = record

        self.__required_variables = metadata.get_required_variables()

        self.__id = self.__record.get("selectionId")

        self.__sp = self.__get_value_or_default(value=self.__record.get("sp"))
        self.__ex = self.__get_value_or_default(value=self.__record.get("ex"))

        self.__set_traded_volume()
        self.__set_ex_back_size()
        self.__set_ex_lay_size()

        self.__set_sp_back_price()

        self.__data = self.__construct_data()

    def get_adapted_data(self):
        return self.__data if self.__is_valid_item() else {}

    def __is_valid_item(self):
        return True if self.__id else False

    def __construct_data(self):
        data = {"id": self.__id}

        if "removal_date" in self.__required_variables:
            data["removal_date"] = self.__get_removal_date()

        if "sp_back_price" in self.__required_variables:
            data["sp_back_price"] = self.__sp_back_price

        if "sp_lay_price" in self.__required_variables:
            data["sp_lay_price"] = self.__get_sp_lay()

        if "sp_back_size" in self.__required_variables:
            data["sp_back_size"] = self.__calc_sp_back_size()

        if "sp_lay_size" in self.__required_variables:
            data["sp_lay_size"] = self.__calc_sp_lay_size()

        if "ex_back_size" in self.__required_variables:
            data["ex_back_size"] = self.__ex_back_size

        if "ex_lay_size" in self.__required_variables:
            data["ex_lay_size"] = self.__ex_lay_size

        if "ex_average_back_price" in self.__required_variables:
            data["ex_average_back_price"] = self.__calc_ex_average_back_price()

        if "ex_average_lay_price" in self.__required_variables:
            data["ex_average_lay_price"] = self.__calc_ex_average_lay_price()

        if "ex_offered_back_price" in self.__required_variables:
            data["ex_offered_back_price"] = self.__get_ex_ex_offered_back_price()

        if "ex_offered_lay_price" in self.__required_variables:
            data["ex_offered_lay_price"] = self.__get_ex_ex_offered_lay_price()

        return data

    def __get_removal_date(self):
        raw_removal_date = self.__record.get("removalDate")
        removal_date = (
            DateTime(raw_removal_date).get_epoch()
            if raw_removal_date
            else not_a_number()
        )
        return removal_date

    def __set_sp_back_price(self):

        if any(
            variable in ["sp_back_price", "sp_lay_price"]
            for variable in self.__required_variables
        ):
            price = self.__sp.get("nearPrice")
            sp_back_price = (
                price if self.__is_valid_price(price=price) else not_a_number()
            )
        else:
            sp_back_price = None
        self.__sp_back_price = sp_back_price
        return None

    def __get_sp_back_price(self):
        return self.__sp_back_price

    def __get_sp_lay(self):
        sp_lay_price = self.__calc_lay_price(self.__sp_back_price)
        return sp_lay_price

    def __set_traded_volume(self):
        traded_volume = self.__ex.get("tradedVolume") if self.__ex else None
        self.__traded_volume = self.__get_value_or_default(
            value=traded_volume, default=[]
        )
        return None

    def __calc_ex_average_back_price(self):
        total_back_price = sum(
            trade.get("size") * trade.get("price") for trade in self.__traded_volume
        )

        ex_average_back_price = (
            total_back_price / self.__ex_back_size
            if self.__ex_back_size
            else not_a_number()
        )
        return ex_average_back_price

    def __calc_ex_average_lay_price(self):
        total_lay_price = sum(
            trade.get("size")
            * (trade.get("price") - 1)
            * self.__calc_lay_price(trade.get("price"))
            for trade in self.__traded_volume
        )

        ex_average_lay_price = (
            total_lay_price / self.__ex_lay_size
            if self.__ex_lay_size
            else not_a_number()
        )
        return ex_average_lay_price

    def __set_ex_back_size(self):
        self.__ex_back_size = (
            sum(trade.get("size") for trade in self.__traded_volume)
            if "ex_back_size" in self.__required_variables
            else None
        )
        return None

    def __calc_sp_back_size(self):
        back_taken = self.__get_value_or_default(
            value=self.__sp.get("backStakeTaken"), default=[]
        )
        sp_back_size = sum(price.get("size") for price in back_taken)
        return sp_back_size

    def __set_ex_lay_size(self):
        self.__ex_lay_size = (
            sum(
                trade.get("size") * (trade.get("price") - 1)
                for trade in self.__traded_volume
            )
            if "ex_lay_size" in self.__required_variables
            else None
        )
        return None

    def __calc_sp_lay_size(self):
        lay_taken = self.__get_value_or_default(
            value=self.__sp.get("layLiabilityTaken"), default=[]
        )
        sp_lay_size = sum(price.get("size") for price in lay_taken)
        return sp_lay_size

    def __get_ex_ex_offered_back_price(self):
        available_to_back = self.__ex.get("availableToBack")
        ex_offered_back_price = (
            available_to_back[0].get("price") if available_to_back else not_a_number()
        )
        return ex_offered_back_price

    def __get_ex_ex_offered_lay_price(self):
        available_to_lay = self.__ex.get("availableToLay")
        ex_offered_lay_price = (
            available_to_lay[0].get("price") if available_to_lay else not_a_number()
        )
        return ex_offered_lay_price

    def __get_value_or_default(self, value, default={}):
        return value or default

    def __calc_lay_price(self, price):
        return 1 / (1 - (1 / price)) if self.__is_valid_price(price) else not_a_number()

    def __is_valid_price(self, price):
        return True if type(price) is float and price > 0 else False
