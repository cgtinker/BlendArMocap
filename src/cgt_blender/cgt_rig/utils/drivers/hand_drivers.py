from dataclasses import dataclass
from math import radians

from .driver_interface import DriverProperties, DriverContainer, DriverType


@dataclass(repr=True)
class Slope:
    slope: float
    min_in: float
    min_out: float

    def __init__(self, min_in, max_in, offset_min, offset_max):
        min_out = min_in + radians(offset_min)
        max_out = max_in + radians(offset_max)

        self.slope = (max_out - min_out) / (max_in - min_in)
        self.min_in = min_in
        self.min_out = min_out


@dataclass(repr=True)
class FingerAngleDriver(DriverProperties):
    target_object: str
    functions: list

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
        # self.functions = ["", "", ""]
        self.functions = [f"{slope.min_out})+{slope.slope}*(-{slope.min_in}+", "", f""]
        self.overwrite = True


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # approx rounded input min max values based on 500 sample values
    # min_input = [0.00573971401900053, 0.02822212688624859, 0.15607228875160217,
    #              0.004682004451751709, 0.004955798387527466, 0.4647256135940552,
    #              0.009591266512870789, 0.380163311958313, 0.009675596840679646,
    #              0.010703802108764648, 0.17845264077186584, 0.016609380021691322,
    #              0.0671580359339714, 0.16959387063980103, 0.2043222188949585]

    # max_input = [0.650924026966095, 0.6996214985847473, 1.1686301231384277,
    #              1.50493586063385, 1.9332847595214844, 1.2798185348510742,
    #              1.5089573860168457, 1.834489345550537, 1.814769983291626,
    #              1.56886887550354, 1.881842851638794, 1.5812692642211914,
    #              1.571094274520874, 1.5308549404144287, 1.8501083850860596]

    # offset_min = [-45, -30, -10,  # thumb
    #               -55, -30, -25,  # index
    #               -30, -40, -15,  # middle
    #               -35, -20, -25,  # ring
    #               -45, -35, -25]  # pinky

    # offset_max = [0, 0, 0,  # thumb
    #               0, 0, 25,  # index
    #               0, 0, 0,  # middle
    #               -25, 0, 0,  # ring
    #               -20, 0, 0]  # pinky

    def __init__(self, driver_targets: list, provider_objs: list):
        # slopes = [Slope(0, 1, 0, 1) for idx, _ in enumerate(self.max_input)]
        # slopes = [Slope(self.min_input[idx], self.max_input[idx], self.offset_min[idx], self.offset_max[idx])
        #          for idx, _ in enumerate(self.max_input)]

        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], slopes[idx]) for idx, _ in
                             enumerate(driver_targets)]
