from app.interface import Interface, abstractfunc

class ExternalAPIInterface(metaclass=Interface):
    @abstractfunc
    def get_data(self):
        pass
