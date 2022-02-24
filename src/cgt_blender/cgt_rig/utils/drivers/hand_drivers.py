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
    # approx input min max values
    # TODO GET CORRECT LIMITS
    in_min = [0.726176545975601, 0.8512987547477319, 0.8664782351964153,
              0.6382369324463897, 1.0161180178300135, 0.8590838794993033,
              0.747025318072078, 0.8319511235545018, 0.7710057722904851,
              0.7691580587764137, 0.805243601965735, 0.9462956763694704,
              0.29239001878315707, 0.3425781593170418, 0.6190174213266966]
    in_max = [1.1829695693631472, 1.4391998285868344, 1.1709237254328397,
              1.1061978605577114, 1.5479205304914194, 1.5351953260841789,
              1.3487873143393585, 1.3620587495339125, 1.3307833220017067,
              1.1376519912105723, 1.2423344583345972, 1.5712642582554004,
              0.3597813181948444, 0.5334325914615673, 0.9812746151850565]
    in_limits = [.0, 3.14]

    # target output min max values
    out_limits = [[-0.6, 3.14], [-0.4, 3.14], [-0.3, 3.14],  # thumb
                  [-0.6, 3.14], [-0.4, 3.14], [-0.3, 3.14],  # index
                  [-0.6, 3.14], [-0.4, 3.14], [-0.3, 3.14],  # middle
                  [-0.6, 3.14], [-0.4, 3.14], [-0.3, 3.14],  # ring
                  [-0.6, 3.14], [-0.4, 3.14], [-0.3, 3.14]]  # pinky

    def __init__(self, driver_targets: list, provider_objs: list):
        # factor and slope start to increase range of motion
        slopes = [[self.out_limits[idx][0],
                   (self.out_limits[idx][1] - self.out_limits[idx][0]) / (
                           self.in_limits[1] - self.in_limits[0])]
                  for idx, _ in enumerate(self.out_limits)]

        self.pose_drivers = [FingerAngleDriver(driver_targets[idx], provider_objs[idx], slopes[idx]) for idx, _ in
                             enumerate(driver_targets)]
