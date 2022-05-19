from dataclasses import dataclass

from ...utils.driver_interface import DriverProperties, DriverContainer, DriverType
from ...utils.bone_prop import CustomBoneProp
from ...utils.mapping import Slope


@dataclass(repr=True)
class EyeDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, driver_target, provider_obj, bone_distance, direction, slope):
        """ Provides eye driver properties to animate the lids. """
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.data_paths = ["scale.z"] * 3
        self.get_functions(direction, bone_distance, slope)
        self.overwrite = True

    def get_functions(self, direction, bone_distance, slope):
        if direction == "down":
            bone_distance *= .65
            self.functions = ["", "",
                              f"{bone_distance}*"
                              f"({slope.name}[0]+(({slope.name}[1] - {slope.name}[0])/({slope.max_in}-{slope.min_in}))*"
                              f"(-{slope.min_in}+(scale)))"
                              ]
        elif direction == "up":
            bone_distance *= .35
            self.functions = ["", "",
                              f"-{bone_distance}*"
                              f"({slope.name}[0]+(({slope.name}[1] - {slope.name}[0])/({slope.max_in}-{slope.min_in}))*"
                              f"(-{slope.min_in}+(scale)))"
                              ]


@dataclass(repr=True)
class EyeDriverContainer(DriverContainer):
    """ Container holding drivers for eye movements. """
    def __init__(self, driver_targets, provider_objs, eye_distances, bone_names):
        inputs = [.0, .5]
        outputs = [-1, 0.0]

        slope = Slope(inputs[0], inputs[1], outputs[0], outputs[1], "up_down")
        self.pose_drivers = []
        for i in range(0, 2):
            for j in range(0, 2):
                self.pose_drivers += [
                    CustomBoneProp(
                        driver_targets[i][j],
                        bone_names[i][j],
                        "location",
                        slope.name,
                        (slope.min_out, slope.max_out))]

        right_top_lid = EyeDriver(driver_targets[0][0], provider_objs[0], eye_distances[0], "down", slope)
        right_bot_lid = EyeDriver(driver_targets[0][1], provider_objs[0], eye_distances[0], "up", slope)
        left_top_lid = EyeDriver(driver_targets[1][0], provider_objs[1], eye_distances[1], "down", slope)
        left_bot_lid = EyeDriver(driver_targets[1][1], provider_objs[1], eye_distances[1], "up", slope)

        self.pose_drivers += [left_top_lid, left_bot_lid, right_top_lid, right_bot_lid]


@dataclass(repr=True)
class MouthCornerDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, driver_target, provider_obj, direction):
        """ Provides mouth corner properties to set up a driver for lip animation. """
        self.target_object = driver_target
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "corner"
        self.driver_type = DriverType.SINGLE
        self.overwrite = True

        if direction == "left":
            self.data_paths = ["scale.x"] * 3
        else:
            self.data_paths = ["scale.z"] * 3

        self.functions = [""] * 3


@dataclass(repr=True)
class MouthDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, driver_target, provider_obj, bone_distance, slope, direction):
        """ Generates lip drivers using custom props. """
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.get_data_paths(direction)
        self.overwrite = True
        self.get_functions(direction, bone_distance, slope)

    def get_data_paths(self, direction):
        if direction in ["up", "down"]:
            self.data_paths = ["scale.z"] * 3
        elif direction in ["left", "right"]:
            self.data_paths = ["scale.x"] * 3

    def get_functions(self, direction, bone_distance, slope):
        if direction in ["up", "down"]:
            self.functions = [
                "",
                "",
                f"-{bone_distance}*"
                f"({slope.name}[0]+(({slope.name}[1] - {slope.name}[0])/({slope.max_in}-{slope.min_in}))*"
                f"(-{slope.min_in}+(scale)))"
            ]
        elif direction in ["left", "right"]:
            if direction == "left":
                sign = "+"
            else:
                sign = "-"
            x_slope = slope[0]
            z_slope = slope[1]
            self.functions = [
                f"{sign}{bone_distance}*"
                f"({x_slope.name}[0]+(({x_slope.name}[1] - {x_slope.name}[0])/({x_slope.max_in}-{x_slope.min_in}))*"
                f"(-{x_slope.min_in}+(scale)))",
                "",
                f"-{bone_distance}*"
                f"({z_slope.name}[0]+(({z_slope.name}[1] - {z_slope.name}[0])/({z_slope.max_in}-{z_slope.min_in}))*"
                f"(-{z_slope.min_in}+(corner)))"
            ]


@dataclass(repr=True)
class MouthDriverContainer(DriverContainer):
    inputs = [
        [.75, .0],  # up
        [0., .75],  # down
        [1.55, 2.425],  # left / right corner
        [-.2, .5],  # up / down corner
    ]
    # [0, 1.5]]  # corners

    outputs = [
        [-.35, .0, "up_map"],
        [0., .10, "down_map"],
        [.0, .10, "left_right"],
        [-.2, .175, "up_down"],
    ]

    def __init__(self, driver_targets, provider_obj, mouth_distances, bone_names):
        """ Generates mouth driver props using custom properties. """
        slopes = [Slope(self.inputs[idx][0], self.inputs[idx][1],
                        self.outputs[idx][0], self.outputs[idx][1], name=self.outputs[idx][2])
                  for idx in range(0, 4)]

        # driver mouth movements (corners and center drivers)
        left_corner = MouthCornerDriver(driver_targets[1][0], provider_obj[1], "left")
        right_corner = MouthCornerDriver(driver_targets[1][1], provider_obj[1], "right")
        upper_lip = MouthDriver(
            driver_targets[0][0], provider_obj[0], mouth_distances[0], slopes[0], "up")
        lower_lip = MouthDriver(
            driver_targets[0][1], provider_obj[0], mouth_distances[0], slopes[1], "down")
        left_lip = MouthDriver(
            driver_targets[1][0], provider_obj[0], mouth_distances[1], (slopes[2], slopes[3]), "left")
        right_lip = MouthDriver(
            driver_targets[1][1], provider_obj[0], mouth_distances[1], (slopes[2], slopes[3]), "right")

        # setting custom bone props for easier value tweaking
        self.pose_drivers = []
        for i in range(0, 2):
            self.pose_drivers += [
                CustomBoneProp(
                    driver_targets[0][i],
                    bone_names[0][i],
                    "location",
                    slopes[i].name,
                    (slopes[i].min_out, slopes[i].max_out))]
            self.pose_drivers += [
                CustomBoneProp(
                    driver_targets[1][i],
                    bone_names[1][::-1][i],
                    "location",
                    slopes[2].name,
                    (slopes[2].min_out, slopes[2].max_out))]
            self.pose_drivers += [
                CustomBoneProp(
                    driver_targets[1][i],
                    bone_names[1][::-1][i],
                    "location",
                    slopes[3].name,
                    (slopes[3].min_out, slopes[3].max_out))]

        self.pose_drivers += [left_corner, right_corner, upper_lip, lower_lip, left_lip, right_lip]


@dataclass(repr=True)
class EyebrowDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, driver_target, provider_obj, bone_distance, target_path, slope):
        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.overwrite = True
        self.data_paths = target_path

        self.functions = [
            "", "",
            f"-{bone_distance}*"
            f"({slope.name}[0]+(({slope.name}[1] - {slope.name}[0])/({slope.max_in}-{slope.min_in}))*"
            f"(-{slope.min_in}+(scale)))"
        ]


@dataclass(repr=True)
class EyebrowDriverContainer(DriverContainer):
    # default slope values for opening and closing eyes
    inputs = [
                 [0.85, 2.0],  # in
                 [0.65, 1.65],  # out
             ] * 2

    outputs = [
                  [-.3, .5],  # in
                  [-.25, .5],  # out
              ] * 2

    def __init__(self, driver_targets, provider_objs, brow_distances, bone_names):
        """ Generates eyebrow driver props using custom properties. """

        # setup slopes
        slopes = [
            Slope(self.inputs[idx][0], self.inputs[idx][1], self.outputs[idx][0], self.outputs[idx][1], "up_down")
            for idx in range(0, 4)
        ]
        tar_path = [
            "scale.x",
            "scale.y",
            "scale.z"
        ]
        self.pose_drivers = []

        # creating expressions containing the props
        self.pose_drivers += [
            CustomBoneProp(
                driver_targets[idx],
                bone_names[idx],
                "location",
                slopes[idx].name,
                (slopes[idx].min_out, slopes[idx].max_out))
            for idx, _ in enumerate(driver_targets)]

        # creating eyebrow drivers using the props
        self.pose_drivers += [
            EyebrowDriver(driver_targets[i], provider_objs[0], brow_distances[i], tar_path, slopes[i])
            for i in range(0, 4)]
