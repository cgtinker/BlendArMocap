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

    def __init__(self,
                 driver_target: str,
                 provider_obj: object,
                 x_slope: Slope,
                 z_slope: Slope):
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
        self.functions = [f"{x_slope.min_out})+{x_slope.slope}*({x_slope.min_in}+",
                          "",
                          f"{z_slope.min_out})+{z_slope.slope}*({z_slope.min_in}+"]
        self.overwrite = True


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # shifting avgs for L / R hand z-angles
    z_inputs_R = [
        [-.7, 18.],  # thumb
        [-1., 10],  # index
        [-3.5, 6.5],  # middle
        [-.5, 10.],  # ring
        [-3, 7.5],  # pinky
    ]

    z_inputs_L = [
        [0.0, 18.],  # thumb
        [0., 8.5],  # index
        [-.9, 7.5],  # middle
        [-.0, 10.],  # ring
        [-3, 7.5],  # pinky
    ]

    z_outputs = [
        # in / out
        [-15, 25],  # thumb
        [-25, 25],  # index
        [0., 30],  # middle
        [5, -30],  # ring
        [5, -35],  # pinky
    ]

    x_inputs = [
        [0.22, 42.76], [0.80, 58.19], [0.59, 93.19],  # thumb
        [5.06, 117.0], [0.66, 116.3], [1.17, 86.71],  # index
        [1.11, 104.8], [0.98, 112.4], [0.41, 111.0],  # middle
        [0.62, 121.3], [1.62, 108.2], [0.05, 99.16],  # ring
        [5.21, 123.9], [2.30, 95.04], [0.71, 117.8]  # pinky
    ]

    x_outputs = [
        [-47.5, 42.76], [-17.5, 58.19], [-12.5, 93.19],  # thumb
        [-62.5, 117.0], [-32.5, 116.3], [-87.5, 86.71],  # index
        [-37.5, 104.8], [-62.5, 112.4], [-12.5, 111.0],  # middle
        [-42.5, 121.3], [-32.5, 108.2], [-27.5, 99.16],  # ring
        [-82.5, 123.9], [-60.0, 95.04], [-37.5, 117.8]  # pinky
    ]

    def __init__(self, driver_targets: list, provider_objs: list, orientation: str):
        x_slopes = [
            Slope(self.x_inputs[idx][0], self.x_inputs[idx][1], self.x_outputs[idx][0], self.x_outputs[idx][1])
            for idx in range(0, 15)
        ]

        z_slopes_R = [
            Slope(self.z_inputs_R[idx][0], self.z_inputs_R[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1])
            for idx in range(0, 5)
        ]

        # values have to be mirrored to fit angles
        self.z_outputs = [[i[0] * -1, i[1] * -1] for idx, i in enumerate(self.z_outputs)]
        m_slopes_L = [
            Slope(self.z_inputs_L[idx][0], self.z_inputs_L[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1])
            for idx in range(0, 5)
        ]

        def get_z_slope(idx):
            if idx not in range(0, 15, 3):
                return Slope(0, 1, 0, 1)

            if orientation == "right":
                return z_slopes_R[int(idx / 3)]
            else:
                return m_slopes_L[int(idx / 3)]

        self.pose_drivers = [
            FingerAngleDriver(
                driver_targets[idx],
                provider_objs[idx],
                x_slopes[idx],
                get_z_slope(idx),
            ) for idx, _ in enumerate(driver_targets)]
