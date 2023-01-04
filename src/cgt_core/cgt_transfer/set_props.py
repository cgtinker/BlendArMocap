from __future__ import annotations

import logging
from typing import List

import bpy

from ..cgt_bpy import cgt_drivers, cgt_bpy_utils
from . import cgt_driver_obj_props


def update_driver_target(obj: bpy.types.Object):
    """ Returns an object which may be used as driver target.
        Deletes object of the same name if it exists. """
    if obj.name + '.D' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj.name + '.D'])
    return cgt_bpy_utils.add_empty(0.1, obj.name + '.D', 'SPHERE')


def set_constraint_props(constraint: bpy.types.Constraint, props: dict):
    logging.debug(f"apply {constraint.name}, {props}")
    for key, value in props.items():
        try:
            setattr(constraint, key, value)
        except AttributeError as err:
            logging.debug(err)


def set_object_remapping_drivers(factory: cgt_drivers.DriverFactory, provider: bpy.types.Object,
                                 remapping_props: List[List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]]):
    """ Set object remapping drivers. """
    d = {'X': 0, 'Y': 1, 'Z': 2}

    id_paths = [
        ['cgt_props.use_loc_x', 'cgt_props.use_loc_y', 'cgt_props.use_loc_z'],
        ['cgt_props.use_rot_x', 'cgt_props.use_rot_y', 'cgt_props.use_rot_z'],
        ['cgt_props.use_sca_x', 'cgt_props.use_sca_y', 'cgt_props.use_sca_z']
    ]

    for props, data_path, m_id_paths in zip(remapping_props, ["location", "rotation_euler", "scale"], id_paths):
        for i, data in enumerate(zip(props, m_id_paths)):
            prop, id_path = data
            if not prop.active:
                continue
            data_path_id = d[prop.remap_details]
            set_default_remapping_driver(factory, provider, data_path, data_path_id, id_path, i)


def set_default_remapping_driver(factory: cgt_drivers.DriverFactory,
                                 provider: bpy.types.Object,
                                 data_path: str, idx: int, id_path: str, from_idx: int):
    """ Set remapping variables and expression.
        :param factory: Any Driver Factory.
        :param provider: Objects yielding properties.
        :param data_path: Data path to map [location, scale, ...]
        :param idx: idx of the data path (None or -1 the data path doesn't point to an array)
        :param id_path: Path to properties (b.e. cgt_props.use_loc_x)
        :param from_idx: Data path id from provider
    """
    factory.add_variable(cgt_drivers.SingleProperty("from_min", provider, f'{id_path}.from_min'), data_path, idx)
    factory.add_variable(cgt_drivers.SingleProperty("from_max", provider, f'{id_path}.from_max'), data_path, idx)
    factory.add_variable(cgt_drivers.SingleProperty("to_min", provider, f'{id_path}.to_min'), data_path, idx)
    factory.add_variable(cgt_drivers.SingleProperty("to_max", provider, f'{id_path}.to_max'), data_path, idx)
    factory.add_variable(cgt_drivers.SingleProperty("factor", provider, f'{id_path}.factor'), data_path, idx)
    factory.add_variable(cgt_drivers.SingleProperty("offset", provider, f'{id_path}.offset'), data_path, idx)

    value_prop = cgt_drivers.TransformChannel("value", provider, data_path, from_idx, "WORLD_SPACE")
    factory.add_variable(value_prop, data_path, idx)

    # TODO check for expansion thingies
    slope = "(to_max - to_min) / (from_max - from_min)"
    offset = f"to_min - {slope} * from_min"
    # value = "{}"
    value = "value"
    expression = f"({slope} * {value} + {offset}) * factor + offset"

    # factory.expand_expression(expression, data_path, idx)
    factory.add_expression(expression, data_path, idx)


def set_chain_driver(prev_obj: bpy.types.Object, obj: bpy.types.Object, previous_driver: bpy.types.Object,
                     factory: cgt_drivers.DriverFactory, distance: float):
    # TODO: use factory instead of driver target

    # SETTING FACTORY VARIBALES
    dist = cgt_drivers.Distance("dist", prev_obj, obj, "WORLD_SPACE", "WORLD_SPACE")
    for i in range(0, 3):
        factory.add_variable(dist, "location", i)

        prop = cgt_drivers.TransformChannel("loc", obj, "location", i, "WORLD_SPACE")
        factory.add_variable(prop, "location", i)

        prop = cgt_drivers.TransformChannel("prev_loc", prev_obj, "location", i, "WORLD_SPACE")
        factory.add_variable(prop, "location", i)

        if previous_driver is not None:
            prop = cgt_drivers.TransformChannel("origin", previous_driver, "location", i, "WORLD_SPACE")
            factory.add_variable(prop, "location", i)
            expression = f"{round(distance, 4)}/dist*(loc-prev_loc)+origin"
        else:
            expression = f"{round(distance, 4)}/dist*(loc-prev_loc)"
        factory.add_expression(expression, "location", i)

    factory.execute()


def set_copy_location_driver(target, factory: cgt_drivers.DriverFactory, space: str = 'WORLD_SPACE'):
    for i in range(0, 3):
        prop = cgt_drivers.TransformChannel("loc", target, "location", i, space)
        factory.add_variable(prop, "location", i)
        factory.add_expression("loc", "location", i)
    factory.execute()

