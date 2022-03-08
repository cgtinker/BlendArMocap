from dataclasses import dataclass
from math import radians

from .driver_interface import DriverProperties, DriverContainer, DriverType


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
    def __init__(self, driver_target: object, provider_obj: object, slope: Slope, z_func: str):
        """ Provides eye driver properties to animate the lids.
            :param provider_obj: object providing rotation values.
            :param slope: factor to multiply and offset the rotation
            :param offset: offsets the base input value
        """

        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "rotation_euler"
        self.property_name = "rotation"
        self.data_paths = ["rotation_euler[0]", "rotation_euler[1]", "rotation_euler[2]"]
        self.functions = [f"{slope.min_out})+{slope.slope}*({slope.min_in}+",
                          "",
                          z_func]
        self.overwrite = True


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # approx rounded input min max values based on 500 sample values
    # min_input = [0.00] * 15
    z_angle_funcs = [
        "-.261+2.5*rotation if rotation != 0 else", "", "",  # thumb
        "-.261+2.5*rotation if rotation != 0 else", "", "",  # index
        "-.055+2.5*rotation if rotation != 0 else", "", "",  # middle
        "0.150-2.5*rotation if rotation != 0 else", "", "",  # ring
        "-.250+5.0*rotation if rotation != 0 else", "", "",  # pinky
    ]

    min_input = [
        0.22, 0.80, 0.59,
        5.06, 0.66, 1.17,
        1.11, 0.98, 0.41,
        0.62, 1.62, 0.05,
        5.21, 2.30, 0.71
    ]

    max_input = [
        42.76, 58.19, 93.19,  # thumb
        117.0, 116.3, 86.71,  # index
        104.8, 112.4, 111.0,  # middle
        121.3, 108.2, 99.16,  # ring
        123.9, 95.04, 117.8  # pinky
    ]

    min_output = [
        -47.5, -17.5, -12.5,  # thumb
        -62.5, -32.5, -87.5,  # index
        -37.5, -62.5, -12.5,  # middle
        -42.5, -32.5, -27.5,  # ring
        -82.5, -60.0, -37.5,  # pinky
    ]

    max_output = [
        42.76, 58.19, 93.19,  # thumb
        117.0, 116.3, 86.71,  # index
        104.8, 112.4, 111.0,  # middle
        121.3, 108.2, 99.16,  # ring
        123.9, 95.04, 117.8  # pinky
    ]

    limits = [0.00] * 15

    def __init__(self, driver_targets: list, provider_objs: list):
        # slopes = [Slope(0, 1, 0, 1)
        #           for idx, _ in enumerate(self.max_input)]
        slopes = [Slope(self.min_input[idx], self.max_input[idx], self.min_output[idx], self.max_output[idx])
                  for idx, _ in enumerate(self.max_input)]

        self.pose_drivers = [
            FingerAngleDriver(
                driver_targets[idx],
                provider_objs[idx],
                slopes[idx],
                self.z_angle_funcs[idx]
            ) for idx, _ in enumerate(driver_targets)]
