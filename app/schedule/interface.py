from app.interface import Interface
from app.singleton import Singleton
from infrastructure.built_in.adapter.abstract_base import abstract_method


class SingletonInterfaceMixin(Singleton, Interface):
    pass


class ScheduleDataInterface(metaclass=SingletonInterfaceMixin):
    @abstract_method
    def get_schedule(self):
        pass
