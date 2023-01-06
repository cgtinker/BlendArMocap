from __future__ import annotations
import bpy
import logging
from ..cgt_utils import cgt_json
from ..cgt_bpy import cgt_bpy_utils, cgt_object_prop


def apply_props2obj(props: dict, obj: bpy.types.Object, target_armature: bpy.types.Object = None):
    if obj == {} or props == {} or target_armature is None:
        return

    for key, value in props:
        if isinstance(value, dict):
            # recv
            apply_props2obj(getattr(props, key, {}), getattr(obj, key, {}), target_armature)

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

                    # adding id as it might be required in some cases and doesn't matter in others
                    target = cgt_bpy_utils.add_empty(0.25, value[0])
                    cgt_object_prop.set_custom_property(target, 'cgt_id', '11b1fb41-1349-4465-b3aa-78db80e8c761')

                    setattr(obj, key, target)

                else:
                    logging.error(f"{value[1]} - Type not supported: {value[1]}.")

        else:
            setattr(obj, key, value)


def load(path: str = None, target_armature: bpy.types.Object = None):
    assert path is not None
    if target_armature is None:
        objs = bpy.context.selected_objects
        assert len(objs) != 0
        assert objs[0].type == 'ARMATURE'
        target_armature = objs[0]

    json_data = cgt_json.JsonData(path)

    for key, d in json_data.__dict__.items():
        # get object target
        obj = cgt_bpy_utils.add_empty(0.01, key)
        if not cgt_object_prop.get_custom_property(obj, 'cgt_id') == '11b1fb41-1349-4465-b3aa-78db80e8c761':
            cgt_object_prop.set_custom_property(obj, 'cgt_id', '11b1fb41-1349-4465-b3aa-78db80e8c761')

        apply_props2obj(d, obj, target_armature)
