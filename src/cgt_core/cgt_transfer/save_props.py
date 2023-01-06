from __future__ import annotations
from typing import List
import bpy
import logging
from . import get_props
from . import object_prop_reflection
from ..cgt_utils import cgt_json


armature_name = None


def convert_object_ptrs2str(cls) -> None:
    """ Pointers to objects to strs (inplace). """
    for key, value in cls.__dict__.items():
        if isinstance(value, object_prop_reflection.RuntimeClass):
            convert_object_ptrs2str(value)
        elif isinstance(value, bpy.types.Object):

            # inform user about target armature
            if value.type == 'ARMATURE':
                global armature_name
                if armature_name is None:
                    armature_name = value.name

                if armature_name != value.name:
                    logging.error(f"Armature targets don't match in cls which may lead to errors when importing: \n{cls}")

            setattr(cls, key, [value.name, value.type])
        else:
            pass


def convert_cls2dict(cls, d: dict) -> None:
    """ Convert cls and subcls to dict """
    for key, value in cls.__dict__.items():
        if isinstance(value, object_prop_reflection.RuntimeClass):
            d[key] = {}
            convert_cls2dict(value, d[key])
        else:
            d[key] = value


def delete_typeof_none(cls) -> None:
    """ Remove ptrs to None (inplace) """
    removable_attrs = []

    for key, value in cls.__dict__.items():
        if isinstance(value, object_prop_reflection.RuntimeClass):
            delete_typeof_none(value)
        elif value is None:
            removable_attrs.append((cls, key))
        else:
            pass

    for cls, key in removable_attrs:
        delattr(cls, key)


def delete_id_data(cls) -> None:
    """ Remove id_data props (internal bpy data used for proper prints) """
    removable_attrs = []

    for key, value in cls.__dict__.items():
        if key == 'id_data':
            removable_attrs.append((cls, key))
        if isinstance(value, object_prop_reflection.RuntimeClass):
            delete_id_data(value)
        else:
            pass

    for cls, key in removable_attrs:
        delattr(cls, key)


def save(objs: List[bpy.types.Object]) -> cgt_json.JsonData:
    """ Saves all avaibale remapping objects, boils down transfer properties to the required minimum. """
    # armature name as helper to check only one armature is used
    global armature_name
    armature_name = None
    properties = {}

    for obj in objs:
        if obj.get('cgt_id') != '11b1fb41-1349-4465-b3aa-78db80e8c761':
            continue

        props = get_props.get_properties_from_object(obj)

        if props.target.target is None:
            continue

        if props.driver_type == 'NONE':
            continue

        # Remove unused remap properties
        remap_props = [
            "use_loc_x", "use_loc_y", "use_loc_z",
            "use_rot_x", "use_rot_y", "use_rot_z",
            "use_sca_x", "use_sca_y", "use_sca_z"
        ]

        for remap_prop in remap_props:
            sub_cls = getattr(props, remap_prop, None)
            if sub_cls is None:
                continue

            if getattr(sub_cls, "active", False):
                continue

            delattr(props, remap_prop)

        # remove unused detail toggles
        detail_toggles = [
            "loc_details", "rot_details", "sca_details"
        ]
        for toggle in detail_toggles:
            if getattr(props, toggle, False):
                continue
            delattr(props, toggle)

        # remove properties set to None
        if props.by_obj.target is None:
            del props.by_obj
        delete_typeof_none(props)

        # convert remaining ptrs to str and cls to dict, then remove id_props
        convert_object_ptrs2str(props)
        id_name = props.id_data
        delete_id_data(props)

        # convert cls to dict
        cls_dict = dict()
        convert_cls2dict(props, cls_dict)

        properties[id_name] = cls_dict

    json_data = cgt_json.JsonData(**properties)
    return json_data


def test():
    objs = bpy.data.objects
    json_data = save(objs)


if __name__ == '__main__':
    test()
