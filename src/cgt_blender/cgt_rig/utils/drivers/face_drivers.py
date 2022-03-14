from dataclasses import dataclass

from .driver_interface import DriverProperties, DriverContainer, DriverType
from ..mapping import Slope


@dataclass(repr=True)
class EyeDriver(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, driver_target, provider_obj, bone_distance, factor, direction):
        """ Provides eye driver properties to animate the lids.
            :param provider_obj: object providing scale values.
            :param target_axis: target axis to set datapath [X, Y, Z].
            :param bone_distance: eye bone distance from rigify rig
            :param factor: factor to multiply the dist
        """
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.data_paths = ["", "", "scale.z"]
        self.get_functions(direction, bone_distance, factor)

    def get_functions(self, direction, bone_distance, factor):
        if direction == "down":
            self.functions = ["", "", f"-{bone_distance}*{factor}+{bone_distance}*"]
        elif direction == "up":
            self.functions = ["", "", f"-{bone_distance}*{factor}*"]


@dataclass(repr=True)
class EyeDriverContainer(DriverContainer):
    def __init__(self, driver_targets, provider_objs, eye_distances):
        right_top_lid = EyeDriver(driver_targets[0][0], provider_objs[0], eye_distances[0], 0.7, "down")
        right_bot_lid = EyeDriver(driver_targets[0][1], provider_objs[0], eye_distances[0], 0.3, "up")
        left_top_lid = EyeDriver(driver_targets[1][0], provider_objs[1], eye_distances[1], 0.7, "down")
        left_bot_lid = EyeDriver(driver_targets[1][1], provider_objs[1], eye_distances[1], 0.3, "up")

        self.pose_drivers = [left_top_lid, left_bot_lid, right_top_lid, right_bot_lid]


@dataclass(repr=True)
class MouthDriver(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, driver_target, provider_obj, bone_distance, factor, direction):
        """ Provides mouth driver properties to animate the lips.
                    :param provider_obj: object providing scale values.
                    :param target_axis: target axis to set datapath [X, Y, Z].
                    :param bone_distance: mouth bone distance from rigify rig
                    :param factor: factor to multiply the dist
                """

        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.get_data_paths(direction)
        self.get_functions(direction, bone_distance, factor)

    def get_data_paths(self, direction):
        if direction in ["up", "down"]:
            self.data_paths = ["", "", "scale.z"]
        elif direction in ["left", "right"]:
            self.data_paths = ["scale.x", "", ""]

    def get_functions(self, direction, bone_distance, factor):
        if direction in ["up", "down"]:
            self.functions = ["", "", f"{bone_distance}*{factor}*"]
        elif direction in ["left", "right"]:
            self.functions = [f"{bone_distance}*{factor}*", "", ""]


@dataclass(repr=True)
class MouthDriverContainer(DriverContainer):
    def __init__(self, driver_targets, provider_obj, mouth_distances):
        upper_lip = MouthDriver(driver_targets[0][0], provider_obj, mouth_distances[0], 0.3, "up")
        lower_lip = MouthDriver(driver_targets[0][1], provider_obj, mouth_distances[0], -0.3, "down")
        left_lip = MouthDriver(driver_targets[1][0], provider_obj, mouth_distances[1], .02, "left")
        right_lip = MouthDriver(driver_targets[1][1], provider_obj, mouth_distances[1], -.02, "right")

        self.pose_drivers = [upper_lip, lower_lip, left_lip, right_lip]


@dataclass(repr=True)
class EyebrowDriver(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, driver_target, provider_obj, bone_distance, target_path, slope):
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.data_paths = target_path
        self.overwrite = True
        self.functions = ["0*", "0*",
                          f"{bone_distance}*.125)-({bone_distance}*.25)*"
                          f"({slope.min_out}+{slope.slope})*({-slope.min_in}+"]


@dataclass(repr=True)
class EyebrowDriverContainer(DriverContainer):
    inputs = [
        [0.85, 2.0],  # in
        [0.65, 1.65],  # mid
        [0.65, 1.65],  # out
    ]

    outputs = [
        # in / out
        [0, 1],  # in
        [0, 1],  # mid
        [0, 1],  # out
    ]

    def __init__(self, driver_targets, provider_objs, brow_distances):
        slopes = [
            Slope(self.inputs[idx][0], self.inputs[idx][1], self.outputs[idx][0], self.outputs[idx][1])
            for idx in range(0, 3)
        ]
        tar_path = [
            ["scale.x", "scale.x", "scale.x"],
            ["scale.y", "scale.y", "scale.y"],
            ["scale.z", "scale.z", "scale.z"]
        ]
        self.pose_drivers = [
            EyebrowDriver(driver_targets[i], provider_objs[0], brow_distances[i], tar_path[i], slopes[i]) if i < 3
            else EyebrowDriver(driver_targets[i], provider_objs[1], brow_distances[i], tar_path[i - 3], slopes[i-3])
            for i in range(0, 6)]
