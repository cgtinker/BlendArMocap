from abc import ABC, abstractmethod
from blender.rig.abs_rigging import DriverType
import bpy


class DriverExpression(ABC):
    driver_target: str
    driver_object: str
    driver_type: DriverType = None
    target_rig: bpy.types.Object = None

    @abstractmethod
    def set_expressions(self):
        pass

