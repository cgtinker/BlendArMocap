from dataclasses import dataclass

from .driver_interface import DriverProperties, DriverContainer, DriverType
from math import radians


@dataclass(repr=True)
class Slope:
    slope: float
    min_in: float
    min_out: float

    def __init__(self, min_in, max_in, min_out, max_out):
        min_in, max_in, min_out, max_out = [radians(value) for value in [min_in, max_in, min_out, max_out]]
        self.slope = (max_out - min_out) / (max_in - min_in)
        self.min_in = min_in
        self.min_out = min_out


@dataclass(repr=True)
class FingerAngleDriver(DriverProperties):
    target_object: str
    functions: list

    # def __init__(self, driver_target, provider_obj, factor, offset):
    def __init__(self, driver_target, provider_obj, slope):
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
        self.functions = [f"{slope.min_out})+{slope.slope}*(-{slope.min_in}+", "", f""]
        self.overwrite = True


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # approx rounded input min max values based on 500 sample values
    min_input = [
        10.5, 10.0, 17.5,  # thumb
        15.0, 5.00, 45.0,  # index
        7.50, 27.5, 6.50,  # middle
        6.50, 17.5, 2.50,  # ring
        15.0, 17.5, 20.0  # pinky
    ]

    max_input = [
        22.5, 42.5, 67.5,  # thumb
        65.0, 95.0, 80.0,  # index
        70.0, 95.0, 105.,  # middle
        70.0, 95.0, 92.5,  # ring
        80.0, 85.0, 105.0  # pinky
    ]

    min_output = [
        -5., -5, -5,     # thumb
        -25, -5, -5,     # index
        -25, -5, -5,     # middle
        -25, -5, -5,     # ring
        -45, -5, -5      # pinky
    ]

    max_output = [
        22.5, 42.5, 67.5,  # thumb
        65.0, 95.0, 80.0,  # index
        70.0, 95.0, 105.,  # middle
        70.0, 95.0, 92.5,  # ring
        80.0, 85.0, 105.0  # pinky
    ]

    def __init__(self, driver_targets: list, provider_objs: list):
        # slopes = [Slope(0, 1, 0, 1) for idx, _ in enumerate(self.max_input)]
        slopes = [Slope(self.min_input[idx], self.max_input[idx], self.min_output[idx], self.max_output[idx])
                  for idx, _ in enumerate(self.max_input)]

        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], slopes[idx]) for idx, _ in
                             enumerate(driver_targets)]
