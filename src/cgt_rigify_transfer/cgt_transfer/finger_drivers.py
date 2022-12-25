from __future__ import annotations
from typing import List, Tuple, Union
import bpy
import logging
from ...cgt_core.cgt_bpy.cgt_drivers import SingleProperty, DriverFactory, TransformChannel
from ...cgt_core.cgt_bpy.cgt_object_prop import set_custom_property, get_custom_property
from ...cgt_core.cgt_bpy import cgt_bpy_utils, cgt_drivers, cgt_object_prop
from .helper import add_remap_properties, add_simple_remap_expression


def remap_property_driver(target: bpy.types.Object, provider: bpy.types.Object, prop_name: str, data_path: str,
                          data_path_idx: int, transform_space: str, mapping: List[float]) -> Tuple[str, str]:
    """ Copy value from provider to target object and remap it using a slope. """
    driver_factory = DriverFactory(target)

    variable = TransformChannel(prop_name, provider, data_path, data_path_idx, transform_space)
    driver_factory.add_variable(variable, data_path, data_path_idx)

    slope_name, offset_name = add_remap_properties(driver_factory, prop_name, *mapping)
    target_driver_factory = add_simple_remap_expression(driver_factory, prop_name, data_path, data_path_idx,
                                                        slope_name, offset_name)
    target_driver_factory.execute()
    return slope_name, offset_name


def link_custom_property(target: Union[bpy.types.PoseBone, bpy.types.Object],
                         provider: Union[bpy.types.PoseBone, bpy.types.Object], prop_name: str):
    """ The provider property gets linked to the target object.
        Only the linked property can be modified. """
    default_value = get_custom_property(provider, prop_name)
    set_custom_property(target, prop_name, default_value)

    # adds a driver to the provider so the value can be adjusted at another place
    driver_factory = DriverFactory(provider)
    prop = SingleProperty(prop_name, target, f'["{prop_name}"]')
    driver_factory.add_variable(prop, f'["{prop_name}"]', -1)
    driver_factory.add_expression(prop_name, f'["{prop_name}"]', -1)
    driver_factory.execute()


def get_driver_object_name(name: str) -> str:
    # TODO: to driver name -> find objects in scene
    return "driver_" + name


def dooo(driver_properties, bone_targets):
    for driver_property in driver_properties:
        # get object references
        provider_obj = cgt_bpy_utils.get_object_by_name(driver_property)
        assert provider_obj is not None

        # get or create driver object
        driver_object_name = get_driver_object_name(driver_property)
        target_obj = cgt_bpy_utils.get_object_by_name(driver_object_name)
        if target_obj is None:
            target_obj = cgt_bpy_utils.add_empty(0.01, driver_object_name)

        # get angle properties for remapping
        angle_properties = []
        for angle_property in driver_properties[driver_property]:
            for angles in driver_properties[driver_property][angle_property]:
                angle_properties.append(driver_properties[driver_property][angle_property][angles])

        # assign drivers
        if len(angle_properties) == 4:
            remap_property_driver(target_obj, provider_obj, "xRot", "rotation", 0,
                                  "WORLD_SPACE", angle_properties[0] + angle_properties[1])
            remap_property_driver(target_obj, provider_obj, "zRot", "rotation", 2,
                                  "WORLD_SPACE", angle_properties[2] + angle_properties[3])

        elif len(angle_properties) == 2:
            remap_property_driver(target_obj, provider_obj, "xRot", "rotation", 0,
                                  "WORLD_SPACE", angle_properties[0] + angle_properties[1])
        else:
            logging.error(f"Angle properties for {target_obj} of {len(angle_properties)} are not supported.")


def do_stuff(targets: List[bpy.types.Object], providers: List[bpy.types.Object], bones: List[bpy.types.PoseBone]):
    prop_name = 'xRot'
    data_path = 'rotation'
    data_path_idx = 0
    transform_space = 'WORLD_SPACE'
    mapping = [0, 1, 2, 3]

    for target, provider, bone in zip(targets, providers, bones):
        slope_name, offset_name = remap_property_driver(
            target, provider, prop_name, data_path, data_path_idx, transform_space, mapping)


def okdoki():
    z_angle_map = [
        [[0.34911, 1.0472], [-0.4363, 0.4363]],
        [[-0.4363, 1.0472], [0.4363, -0.6981]],
        [[-0.6109, 0.6981], [0.6109, -0.4363]],
        [[-0.4363, 0.6981], [0.1745, -0.5236]],
        [[-0.6981, 0.8727], [0.3491, -0.5236]]
    ]
    x_angle_map = [
        [[[0.011, 0.63], [-0.6, 0.63]], [[0.01, 0.536], [-0.3, 0.54]], [[0.008, 1.035], [-0.15, 1.03]]],
        [[[0.105, 1.331], [-0.5, 1.33]], [[0.014, 1.858], [-0.2, 1.86]], [[0.34, 1.523], [-0.55, 1.52]]],
        [[[0.046, 1.326], [-0.5, 1.33]], [[0.33, 1.803], [-0.3, 1.8]], [[0.007, 1.911], [-0.15, 1.91]]],
        [[[0.012, 1.477], [-0.6, 1.48]], [[0.244, 1.674], [-0.3, 1.67]], [[0.021, 1.614], [-0.3, 1.61]]],
        [[[0.12, 1.322], [-0.8, 1.32]], [[0.213, 1.584], [-0.5, 1.58]], [[0.018, 1.937], [-0.3, 1.94]]]
    ]