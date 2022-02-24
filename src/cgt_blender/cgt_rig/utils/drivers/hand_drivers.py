from dataclasses import dataclass

from .driver_interface import DriverProperties, DriverContainer, DriverType


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
        self.overwrite = True
        self.provider_obj = provider_obj
        self.property_type = "rotation_euler"
        self.property_name = "rotation"
        self.data_paths = ["rotation_euler[0]", "rotation_euler[1]", "rotation_euler[2]"]
        self.functions = [f"{slope[0]}+{slope[1]}*", "", f""]


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # approx rounded input min max values based on 500 sample values
    in_min = [0.365, 0.304, 0.562,
              0.189, 0.481, 0.197,
              0.277, 0.370, 0.229,
              0.585, 0.387, 0.386,
              0.215, 0.225, 0.272]

    in_max = [1.443, 1.360, 0.934,
              1.285, 1.525, 1.207,
              1.568, 1.260, 1.051,
              1.433, 1.190, 1.256,
              0.501, 0.523, 0.787]

    out_min = [-0.366, 0.304, 0.562,
               -0.189, 0.481, 0.197,
               -0.277, 0.370, 0.229,
               -0.585, 0.387, 0.386,
               -0.215, 0.225, 0.272]

    out_max = [1.443, 1.360, 0.934,  # thumb
               1.285, 1.525, 1.207,  # index
               1.568, 1.260, 1.051,  # middle
               1.433, 1.190, 1.256,  # ring
               0.501, 0.523, 0.787]  # pinky

    def __init__(self, driver_targets: list, provider_objs: list):
        # factor and slope start to increase range of motion
        slopes = [[self.out_min[idx],
                   (self.out_max[idx] - self.out_min[idx]) / (
                           self.in_max[idx] - self.in_min[idx])]
                  for idx, _ in enumerate(self.out_min)]

        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], slopes[idx]) for idx, _ in
                             enumerate(driver_targets)]
