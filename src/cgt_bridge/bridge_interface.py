from abc import ABC, abstractmethod
from ..cgt_naming import COLLECTIONS


class CustomData:
    idx = None
    loc = None
    rot = None
    sca = None
    obj = None


class BridgeInterface(ABC):
    parent_col = COLLECTIONS.drivers
    prev_rotation = {}

    @abstractmethod
    def get_instances(self):
        pass

    @abstractmethod
    def set_position(self, data, frame):
        pass

    @abstractmethod
    def set_rotation(self, data, frame):
        pass

    @abstractmethod
    def set_scale(self, data, frame):
        pass
