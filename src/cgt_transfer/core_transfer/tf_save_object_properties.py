from __future__ import annotations
from typing import List
import bpy
import logging
from . import tf_get_object_properties, tf_reflect_object_properties
from ...cgt_core.cgt_utils import cgt_json

armature_name = None


def convert_object_ptrs2str(cls) -> None:
    """ Pointers to objects to strs (inplace). """
    for key, value in cls.__dict__.items():
        if isinstance(value, tf_reflect_object_properties.RuntimeClass):
            convert_object_ptrs2str(value)
        elif isinstance(value, bpy.types.Object):

            # inform user about target armature
            if value.type == 'ARMATURE':
                global armature_name
                if armature_name is None:
                    armature_name = value.name

                if armature_name != value.name:
                    logging.warning(
                        f"Armature targets don't match in cls which may lead to errors when importing: \n{cls}")

            setattr(cls, key, [value.name, value.type])
        else:
            pass


def convert_cls2dict(cls, d: dict) -> None:
    """ Convert cls and subcls to dict """
    for key, value in cls.__dict__.items():
        if isinstance(value, tf_reflect_object_properties.RuntimeClass):
            d[key] = {}
            convert_cls2dict(value, d[key])
        else:
            d[key] = value


def delete_typeof_none(cls) -> None:
    """ Remove ptrs to None (inplace) """
    removable_attrs = []

    for key, value in cls.__dict__.items():
        if isinstance(value, tf_reflect_object_properties.RuntimeClass):
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
        if isinstance(value, tf_reflect_object_properties.RuntimeClass):
            delete_id_data(value)
        else:
            pass

    for cls, key in removable_attrs:
        delattr(cls, key)


def save(objs: List[bpy.types.Object]) -> cgt_json.JsonData:
    """ Saves all available remapping objects, boils down transfer properties to the required minimum. """
    # TODO: SAVING MUST CHECK X AXIS WHEN USING DEFAULT REMAP VALUES
    # armature name as helper to check only one armature is used
    global armature_name
    armature_name = None
    properties = {}

    for obj in objs:
        if obj.get('cgt_id') != '11b1fb41-1349-4465-b3aa-78db80e8c761':
            continue

        props = tf_get_object_properties.get_properties_from_object(obj)

        if props.target.target is None:
            continue

        if props.driver_type == 'NONE':
            continue

        # Remove unused remap properties
        remap_props = [
            ["use_loc_x", "use_loc_y", "use_loc_z"],
            ["use_rot_x", "use_rot_y", "use_rot_z"],
            ["use_sca_x", "use_sca_y", "use_sca_z"]
        ]

        detail_toggles = [
            "loc_details", "rot_details", "sca_details"
        ]

        remap_defaults = {
            "factor":        1.0,
            "offset":        0.0,
            "from_min":      0.0,
            "from_max":      1.0,
            "to_min":        0.0,
            "to_max":        1.0
        }

        # keep x values if details aren't used, remove inactive remap props
        for remap_prop, details in zip(remap_props, detail_toggles):
            use_details = getattr(props, details, False)
            if not use_details:
                delattr(props, details)

            for i, axis in enumerate(remap_prop):
                # remove default values
                sub_cls = getattr(props, axis, None)
                for key, value in remap_defaults.items():
                    if not getattr(sub_cls, key, value) == value:
                        continue
                    delattr(sub_cls, key)

                # keep x-remap-props if not use details
                if not use_details and i == 0:
                    continue

                # check cls
                if sub_cls is None:
                    continue

                if getattr(sub_cls, "active", False):
                    continue

                # del cls
                delattr(props, axis)

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

        # get constraints
        constraints = [(c.type, tf_get_object_properties.get_constraint_props(c)) for c in obj.constraints]

        # id_name contains 'object name' and 'object type', get in first lvl depth for easier loading
        properties[id_name[0]] = {}
        properties[id_name[0]]['cgt_props'] = cls_dict
        properties[id_name[0]]['constraints'] = constraints

        if obj.users_collection:
            properties[id_name[0]]['collection'] = obj.users_collection[0].name
        else:
            properties[id_name[0]]['collection'] = "cgt_DRIVERS"

    json_data = cgt_json.JsonData(**properties)
    return json_data


def test():
    objs = bpy.data.objects
    json_data = save(objs)


if __name__ == '__main__':
    test()
