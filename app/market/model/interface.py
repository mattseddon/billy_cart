from app.interface import Interface
from infrastructure.built_in.adapter.abstract_base import abstract_method


class WeightedLinearRegressionInterface(metaclass=Interface):
    @abstract_method
    def get_alpha(self):
        pass

    @abstract_method
    def get_Beta(self):
        pass
