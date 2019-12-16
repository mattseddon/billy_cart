from app.interface import Interface
from app.singleton import Singleton
from infrastructure.class_construction.abstract_base import abstract_method


class SingletonInterfaceMixin(Singleton, Interface):
    pass


class ExternalAPIScheduleInterface(metaclass=SingletonInterfaceMixin):
    @abstract_method
    def get_schedule(self):
        pass
