from .driver_interface import Expression
from ...abs_rigging import DriverType


class JointLength(Expression):
    def set(self):
        self.property_type = "location"
        self.property_name = "length"
        self.data_paths = ["scale.z", "scale.z", "scale.z"]
        self.functions = ["", "", ""]


class JointHead(Expression):
    def set(self):
        self.property_type = "location"
        self.property_name = "prev_pos"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class DriverOrigin(Expression):
    def set(self):
        self.property_type = "location"
        self.property_name = "origin"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class MainLimbDriver(Expression):
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

    def set(self):
        self.property_type = "location"
        self.property_name = "loc"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = [f"({self.offset[0]}+origin))+{self.length}/(length)*(-(prev_pos)+",
                          f"({self.offset[1]}+origin))+{self.length}/(length)*(-(prev_pos)+",
                          f"({self.offset[2]}+origin))+{self.length}/(length)*(-(prev_pos)+"]


class PoseDriver(Expression):
    name: str = None
    driver_type: DriverType = DriverType.limb_driver
    length: float = .0
    offset: list = [.0, .0, .0]
    expressions: list = None

    def set(self):
        pass

    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_detected_joint_length_expression(driver_target):
        return [
            driver_target, "location", "length",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]
        ]

    @staticmethod
    def get_detected_joint_head_expression(driver_target):
        return [
            driver_target, "location", "prev_pos",
            ["location.x", "location.y", "location.z"],
            ["", "", ""]
        ]

    @staticmethod
    def get_driver_origin_expression(driver_target):
        return [
            driver_target, "location", "origin",
            ["location.x", "location.y", "location.z"],
            ["", "", ""]
        ]

    def get_driver_main_expression(self, driver_target):
        return [
            driver_target, "location", "loc",
            ["location.x", "location.y", "location.z"],
            [f"({self.offset[0]}+origin))+{self.length}/(length)*(-(prev_pos)+",
             f"({self.offset[1]}+origin))+{self.length}/(length)*(-(prev_pos)+",
             f"({self.offset[2]}+origin))+{self.length}/(length)*(-(prev_pos)+"]
        ]