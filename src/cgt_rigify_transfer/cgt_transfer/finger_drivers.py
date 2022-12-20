from __future__ import annotations
from typing import List
import bpy
from ...cgt_core.cgt_bpy.cgt_drivers import SingleProperty, DriverFactory, TransformChannel
from .helper import add_remap_properties, add_simple_remap_expression


def remap_property_driver(target: bpy.types.Object, provider: bpy.types.Object, prop_name: str,
                          data_path: str, data_path_idx: int, transform_space: str, mapping: List[float]):
    """ Copy value from provider to target object and remap it using a slope. """
    target_driver_factory = DriverFactory(target)

    variable = TransformChannel(prop_name, provider, data_path, data_path_idx, transform_space)
    target_driver_factory.add_variable(variable, data_path, data_path_idx)

    slope_name, offset_name = add_remap_properties(target_driver_factory, prop_name, *mapping)
    target_driver_factory = add_simple_remap_expression(target_driver_factory, prop_name, data_path, data_path_idx,
                                                        slope_name, offset_name)
    target_driver_factory.execute()


def xAngles(x_inputs, x_outputs):
    for x_in, x_out in zip(x_inputs, x_outputs):
        mapping = x_in + x_out  # flatten
        

def do_stuff(targets: List[bpy.types.Object], providers: List[bpy.types.Object], bones: List[bpy.types.PoseBone]):
    prop_name = 'xRot'
    data_path = 'rotation'
    data_path_idx = 0
    transform_space = 'WORLD_SPACE'
    mapping = [0, 1, 2, 3]

    for target, provider, bone in zip(targets, providers, bones):
        remap_property_driver(target, provider, prop_name, data_path, data_path_idx, transform_space, mapping)


class FingerDrivers:
    # order: thumb / index / middle / ring / pinky
    # slope values for z-angles in degrees
    z_inputs = [[0.3491, 1.0472], [-0.4363, 1.0472], [-0.6109, 0.6981], [-0.4363, 0.6981], [-0.6981, 0.8727]]
    z_outputs = [[-0.4363, 0.4363], [0.4363, -0.6981], [0.6109, -0.4363], [0.1745, -0.5236], [0.3491, -0.5236]]

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
