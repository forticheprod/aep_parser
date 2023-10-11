import abc
import sys


if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(
        'ABC', (object,),
        {'__slots__': ()}
    )


class FootageSource(ABC):
    def __init__(self):
        # TODO conformFrameRate
        # TODO displayFrameRate
        # TODO isStill
        # TODO nativeFrameRate
        pass

    def __repr__(self):
        return str(self.__dict__)
