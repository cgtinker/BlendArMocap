from .driver_interface import DriverProperties, DriverContainer, DriverType
from dataclasses import dataclass


@dataclass(repr=True)
class FingerAngleDriver(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, driver_target, provider_obj, factor):
        """ Provides eye driver properties to animate the lids.
            :param provider_obj: object providing rotation values.
            :param factor: factor to multiply and offset the rotation
        """
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "rotation_euler"
        self.property_name = "rotation"
        self.data_paths = ["rotation_euler[0]", "rotation_euler[1]", "rotation_euler[2]"]
        self.functions = [f"rotation*{factor})-(.5*{factor}*", "", f""]


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    def __init__(self, driver_targets, provider_objs):
        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], 1.5) for idx, _ in
                             enumerate(driver_targets)]
