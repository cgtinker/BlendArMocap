from dataclasses import dataclass
from math import radians, pi

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
        self.functions = ["", "", ""]
        # self.functions = [f"{slope.min_out})+{slope.slope}*(-{slope.min_in}+", "", f""]
        # self.overwrite = True


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # approx rounded input min max values based on 500 sample values
    max_input = [1.9715394063973906, 1.9409170241817724, 1.4748038424967593,
                 1.7566168258592543, 2.1689891426008736, 2.1262475482542937,
                 2.149778283059359, 1.6966564713452934, 1.6139473430520546,
                 1.9004418271158388, 1.677868759613463, 1.9729289188813925,
                 1.2514007521534158, 1.0305037375320294, 1.7108675958114072]

    min_input = [0.01633764528093298, 0.013827483686734154, 0.0691940389377162,
                 0.005643529841509901, 0.004684739070137908, 0.00934261444783632,
                 0.019570586743391565, 0.008847253634802304, 0.005353900408103954,
                 0.009209944768346605, 0.013687051320355704, 0.014263744947147612,
                 0.007851238324285822, 0.018652939267497854, 0.020807922400291265]

    offset_min = [-45, -20, -10,  # thumb
                  -45, -25, -85,  # index
                  -35, -55, -15,  # middle
                  -45, -30, -25,  # ring
                  -55, -55, -25]  # pinky

    offset_max = [45, 45, 0,  # thumb
                  0, 0, 75,  # index
                  15, 0, 0,  # middle
                  -25, 0, 15,  # ring
                  -40, 0, 0]  # pinky

    def __init__(self, driver_targets: list, provider_objs: list):
        slopes = [Slope(0, 1, 0, 1) for idx, _ in enumerate(self.max_input)]
        #slopes = [Slope(self.min_input[idx], self.max_input[idx], self.offset_min[idx], self.offset_max[idx])
        #          for idx, _ in enumerate(self.max_input)]

        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], slopes[idx]) for idx, _ in
                             enumerate(driver_targets)]
