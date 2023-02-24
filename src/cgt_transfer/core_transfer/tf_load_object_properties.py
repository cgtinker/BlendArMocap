from __future__ import annotations
import bpy
from typing import Union, Any
import logging
from ...cgt_core.cgt_utils import cgt_json
from ...cgt_core.cgt_bpy import cgt_bpy_utils, cgt_object_prop, cgt_collection


def idle_object_props(props):
    """ Set CGT_Object_Properties to Idle State. """
    def value_mapping(values):
        values.active = False
        for val in ['factor', 'from_max', 'to_max']:
            setattr(values, val, 1.0)
        for val in ['offset', 'from_min', 'to_min']:
            setattr(values, val, 0.0)

    props.active = False
    props.driver_type = 'NONE'
    for details in ['loc_details', 'rot_details', 'sca_details']:
        setattr(props, details, False)
    for target in ['to_obj', 'from_obj', 'remap_from_obj', 'remap_to_obj']:
        setattr(props, target, None)

    for transform in ['rot', 'loc', 'sca']:
        paths = [f"use_{transform}_{axis}" for axis in ['x', 'y', 'z']]
        for path in paths:
            values = getattr(props, path, None)
            if values is None:
                continue
            value_mapping(values)

    props.target.target = None
    props.by_obj.target = None


def apply_props2obj(props: dict, obj: Union[bpy.types.Object, bpy.types.Constraint], target_armature: bpy.types.Object = None):
    """ Apply CGT_Object_Properties stored state. """
    if obj == {} or props == {} or target_armature is None:
        return

    for key, value in props.items():
        if isinstance(value, dict):     # recv
            apply_props2obj(value, getattr(obj, key, {}), target_armature)

        elif isinstance(value, list):
            # obj types are declared at 2nd idx in a list
            if len(value) != 2:
                setattr(obj, key, value)
            else:
                if value[1] == 'ARMATURE':
                    setattr(obj, key, target_armature)

                elif value[1] in ['EMPTY', 'MESH', 'CURVE', 'SURFACE', 'META', 'FONT',
                                  'POINTCLOUD', 'VOLUME', 'GPENCIL', 'LATTICE', 'LIGHT',
                                  'LIGHT_PROBE', 'CAMERA', 'SPEAKER', 'CURVES']:
                    # handling default objects and other kinds of ptrs
                    if cgt_bpy_utils.get_object_by_name(value[0]) is None:
                        logging.warning(f"Object of type {value[1]} doesn't exist - creating {value[1]} as EMPTY.")

                    # adding id as it might be required in some cases and hopefully doesn't matter in others
                    target = cgt_bpy_utils.add_empty(0.25, value[0])
                    cgt_object_prop.set_custom_property(target, 'cgt_id', '11b1fb41-1349-4465-b3aa-78db80e8c761')

                    try:
                        setattr(obj, key, target)
                    except AttributeError as err:
                        logging.warning(err)

                else:
                    logging.error(f"{value[1]} - Type not supported: {value[1]}.")

        else:
            try:
                setattr(obj, key, value)
            except (AttributeError, TypeError) as err:
                logging.warning(err)


def apply_constraints(constraints: list, obj: bpy.types.Object, target_armature: bpy.types.Object):
    """ Add stored constraints to objects. """
    if obj == {} or len(constraints) == 0:
        return

    # storing constraints as list of [constraint_name, constraint_properties]
    for name, props in constraints:
        constraint = obj.constraints.new(name)
        apply_props2obj(props, constraint, target_armature)


# TODO: Col polling unused
def load(objects: Any, path: str = None, target_armature: bpy.types.Object = None):
    """ Load CGT_Object_Properties and Constraints from json and apply the data. """
    assert path is not None
    if target_armature is None:
        _objs = bpy.context.selected_objects
        assert len(_objs) != 0
        assert _objs[0].type == 'ARMATURE'
        target_armature = _objs[0]

    json_data = cgt_json.JsonData(path)

    # clean existing objs
    for ob in objects:
        if cgt_object_prop.get_custom_property(ob, 'cgt_id') is None:
            continue
        ob.constraints.clear()
        idle_object_props(ob.cgt_props)

    for key, d in json_data.__dict__.items():
        # only link if collection exists
        if bpy.data.collections.get(d['collection'], None) is None:
            continue

        # get object target
        obj = objects.get(key, None)
        if obj is None:
            obj = cgt_bpy_utils.add_empty(0.01, key)

        if cgt_object_prop.get_custom_property(obj, 'cgt_id') is None:
            # TODO: cgt id shouldn't be that long tag - maybe switch to key in the future and just check if any id
            cgt_object_prop.set_custom_property(obj, 'cgt_id', '11b1fb41-1349-4465-b3aa-78db80e8c761')
            cgt_collection.add_object_to_collection(d['collection'], obj)

        # apply data
        apply_props2obj(d['cgt_props'], obj.cgt_props, target_armature)
        apply_constraints(d['constraints'], obj, target_armature)