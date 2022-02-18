from .driver_interface import DriverProperties
from ...abs_rigging import DriverType
from ....utils import objects


class JointLength(DriverProperties):
    def __init__(self, provider_obj, **kwargs):
        self.provider_obj = provider_obj
        self.driver_type = DriverType.single_prop
        self.property_type = "location"
        self.property_name = "length"
        self.data_paths = ["scale.z", "scale.z", "scale.z"]
        self.functions = ["", "", ""]


class PreviousPosition(DriverProperties):
    def __init__(self, provider_obj, **kwargs):
        self.provider_obj = provider_obj
        self.driver_type = DriverType.single_prop
        self.property_type = "location"
        self.property_name = "prev_pos"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class DriverOrigin(DriverProperties):
    def __init__(self, provider_obj, **kwargs):
        self.provider_obj = provider_obj
        self.driver_type = DriverType.single_prop
        self.property_type = "location"
        self.property_name = "origin"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class MainExpression(DriverProperties):
    offset: list = [.0, .0, .0]

    def __init__(self, provider_obj, **kwargs):
        self.provider_obj = provider_obj
        self.driver_type = DriverType.single_prop
        self.property_type = "location"
        self.property_name = "loc"
        self.data_paths = ["location.x", "location.y", "location.z"]

        # offset by object
        if kwargs['offset'] is not None:
            ob = objects.get_object_by_name(self.provider_obj)
            tar = ob.location
            self.offset = kwargs['offset'] - tar

        self.functions = [f"({self.offset[0]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+",
                          f"({self.offset[1]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+",
                          f"({self.offset[2]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+"]


class LimbDriver:
    joint_head: PreviousPosition
    joint_length: JointLength
    joint_tail: MainExpression
    driver_origin: DriverOrigin

    pose_drivers: list = None

    def __init__(self, driver_target, driver_origin, detected_joint, rigify_joint_length, driver_offset):
        self.driver_target = driver_target
        # previous driver as origin
        self.driver_origin = DriverOrigin(driver_origin)

        # detected results for mapping
        self.joint_head = PreviousPosition(detected_joint[0])
        self.joint_length = JointLength(detected_joint[1])
        self.joint_tail = MainExpression(detected_joint[1], offset=driver_offset, length=rigify_joint_length)

        self.pose_drivers = [self.driver_origin, self.joint_head, self.joint_length, self.joint_tail]
        for driver in self.pose_drivers:
            driver.target_object = driver_target
