'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from dataclasses import dataclass
from math import radians

from ..utils.bone_prop import CustomBoneProp
from ..utils.driver_interface import DriverProperties, DriverContainer, DriverType, ObjectType
from ..utils.mapping import Slope, CustomProps


@dataclass(repr=True)
class FingerAngleDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self,
                 driver_target: str,
                 provider_obj: object,
                 x_slope: Slope,
                 z_slope: Slope):
        """ Provides finger driver properties to animate the x- & z-angles.
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
        self.functions = [
            f"{x_slope.name}[0]+(({x_slope.name}[1] - "
            f"{x_slope.name}[0])/({x_slope.max_in}-{x_slope.min_in}))*({-x_slope.min_in}+(rotation))",
            "",
            f"{z_slope.name}[0]+(({z_slope.name}[1] - "
            f"{z_slope.name}[0])/({x_slope.max_in}-{x_slope.min_in}))*({-z_slope.min_in}+(rotation))"
        ]


@dataclass(repr=True)
class DefaultFingerAngleDriver(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self,
                 driver_target: str,
                 provider_obj: object,
                 x_slope: Slope):
        """ Provides finger driver properties to animate the x-angles.
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
        self.functions = [
            f"{x_slope.name}[0]+(({x_slope.name}[1] - "
            f"{x_slope.name}[0])/({x_slope.max_in}-{x_slope.min_in}))*({-x_slope.min_in}+(rotation))",
            "",
            ""
        ]


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # matrix order: thumb / index / middle / ring / pinky

    # slope values for z-angles in degrees
    z_inputs = [
        [20, 60],
        [-25, 60],
        [-35, 40],
        [-25, 40],
        [-40, 50],
    ]

    z_outputs = [
        [-25, 25.],
        [25., -40],
        [35., -25],
        [10., -30],
        [20., -30],
    ]

    # slope values for x-angles in radians
    x_inputs = [
        [0.011, 0.630], [0.010, 0.536], [0.008, 1.035],
        [0.105, 1.331], [0.014, 1.858], [0.340, 1.523],
        [0.046, 1.326], [0.330, 1.803], [0.007, 1.911],
        [0.012, 1.477], [0.244, 1.674], [0.021, 1.614],
        [0.120, 1.322], [0.213, 1.584], [0.018, 1.937]
    ]

    x_outputs = [
        [-.60, 0.63], [-.30, 0.54], [-.15, 1.03],
        [-.50, 1.33], [-.20, 1.86], [-.55, 1.52],
        [-.50, 1.33], [-.30, 1.80], [-.15, 1.91],
        [-.60, 1.48], [-.30, 1.67], [-.30, 1.61],
        [-.80, 1.32], [-.50, 1.58], [-.30, 1.94]
    ]

    def __init__(self, driver_targets: list, provider_objs: list, orientation: str, bone_names: list):
        """ Generates driver properties for fingers using custom properties. """
        # generate slopes for x angles
        x_slopes = [
            Slope(self.x_inputs[idx][0], self.x_inputs[idx][1], self.x_outputs[idx][0], self.x_outputs[idx][1], "x_map")
            for idx in range(0, 15)
        ]

        # preparing slope input values for z-angles
        self.z_inputs_r = [[radians(v[0]), radians(v[1])] for v in self.z_inputs]
        self.z_inputs_l = [[radians(v[0]), radians(v[1])] for v in self.z_inputs]
        self.z_outputs = [[radians(v[0]), radians(v[1])] for v in self.z_outputs]

        # generate z slopes for the right hand
        z_slopes_r = [
            Slope(self.z_inputs_r[idx][0], self.z_inputs_r[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1],
                  "z_map")
            for idx in range(0, 5)
        ]

        # values have to be mirrored to fit angles (for left and right hand)
        self.z_outputs = [[i[0] * -1, i[1] * -1] for idx, i in enumerate(self.z_outputs)]
        z_slopes_l = [
            Slope(self.z_inputs_l[idx][0], self.z_inputs_l[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1],
                  "z_map")
            for idx in range(0, 5)
        ]

        # helper method to access the slopes
        def get_z_slope(idx):
            if idx not in range(0, 15, 3):
                return Slope(0, 1, 0, 1)

            if orientation == "right":
                return z_slopes_r[int(idx / 3)]
            else:
                return z_slopes_l[int(idx / 3)]

        self.pose_drivers = []

        # adding driver using x props
        for idx, _ in enumerate(driver_targets):
            # x-angle custom prop
            self.pose_drivers.append(CustomBoneProp(driver_targets[idx],
                                                    bone_names[idx],
                                                    "rotation_euler",
                                                    x_slopes[idx].name,
                                                    (x_slopes[idx].min_out, x_slopes[idx].max_out)))
            # default finger angle drivers use only x-prop
            if idx % 3 != 0:
                self.pose_drivers.append(DefaultFingerAngleDriver(driver_targets[idx],
                                                                  provider_objs[idx],
                                                                  x_slopes[idx]))
            else:
                # mcps contain also z-angles
                self.pose_drivers.append(CustomBoneProp(
                    driver_targets[idx],
                    bone_names[idx],
                    "rotation_euler",
                    get_z_slope(idx).name,
                    (get_z_slope(idx).min_out, get_z_slope(idx).max_out)
                ))

                self.pose_drivers.append(FingerAngleDriver(driver_targets[idx],
                                                           provider_objs[idx],
                                                           x_slopes[idx],
                                                           get_z_slope(idx)))
