from abc import ABCMeta, ABC


class AbstractBaseMetaclass(ABCMeta):
    pass


class AbstractBaseClass(ABC):
    pass


def abstract_method(method):
    method.__isabstractmethod__ = True
    return method
