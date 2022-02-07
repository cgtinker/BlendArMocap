from _blender.rig.abs_rigging import DriverType
import bpy


class PoseDriver:
    name: str = None
    driver_type: DriverType = DriverType.limb_driver
    length: float = .0
    offset: list = [.0, .0, .0]
    expressions: list = None
    target_rig: bpy.types.Object = None

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