from __future__ import annotations
from typing import Tuple, Any, Optional, List
import bpy
from . import cgt_reflect_driver_properties, cgt_driver_obj_props


def get_properties_from_object(obj: bpy.types.Object) -> Tuple[
    bpy.types.Object, cgt_reflect_driver_properties.RuntimeClass()]:
    properties = cgt_reflect_driver_properties.get_attributes(
        cgt_reflect_driver_properties.cls_type_dict["OBJECT_PGT_CGT_TransferProperties"],
        obj.cgt_props,
        cgt_reflect_driver_properties.RuntimeClass()
    )

    return obj, properties


def validate_obj_properties(obj, properties) -> bool:
    pass


def get_target(tar_props: cgt_driver_obj_props.OBJECT_PGT_CGT_TransferTarget) -> Tuple[
    Optional[bpy.types.Object], Optional[Any], str]:
    if tar_props.target is None:
        return None, None, 'ABORT'

    if tar_props.obj_type == 'ANY':
        return tar_props.target, None, 'ANY'

    elif tar_props.obj_type == 'MESH':
        if tar_props.object_type == 'OBJECT':
            return tar_props.target, None, 'OBJECT'

        elif tar_props.object_type == 'SHAPE_KEY':
            if tar_props.target_shape_key not in tar_props.target.data.shape_keys.key_blocks:
                return None, None, 'ABORT'
            return tar_props.target, tar_props.target.data.shape_keys.key_blocks[
                tar_props.target_shape_key], 'SHAPE_KEY'

    elif tar_props.obj_type == 'ARMATURE':
        if tar_props.armature_type == 'ARMATURE':
            return tar_props.target, None, 'ARMATURE'

        elif tar_props.armature_type == 'BONE':
            if tar_props.target_bone not in tar_props.target.pose.bones:
                return None, None, 'ABORT'
            return tar_props.target, tar_props.target.pose.bones[tar_props.target_bone], 'BONE'

    assert RuntimeError, 'Type not defined.'


def validate_value_mapping_props(props: List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]):
    if props[0].remap_details == props[1].remap_details or props[0].remap_details == props[2].remap_details or props[1].remap_details == props[2].remap_details:
        return False


def set_detailed_value_remap(props: List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]):
    def validate_mapping_properties():
        pass
    pass


def set_default_value_remap(props: cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping):
    pass


def get_transfer_props(properties: cgt_driver_obj_props.OBJECT_PGT_CGT_TransferProperties):
    tar_ob, sub_tar, tar_type = get_target(properties.target)
    if tar_type == 'ABORT':
        return

    # TODO: remapping as boolean would be preferred
    loc_xyz = [properties.loc_details, [properties.use_loc_x, properties.use_loc_y, properties.use_loc_z]]
    rot_xyz = [properties.rot_details, [properties.use_rot_x, properties.use_rot_y, properties.use_rot_z]]
    sca_xyz = [properties.sca_details, [properties.use_sca_x, properties.use_sca_y, properties.use_sca_z]]

    # TODO: recheck, I think this is way more complex than it looks atm
    # TODO: Apply drivers directly if possible???? Prolly write expression etc first
    for details, props in [loc_xyz, rot_xyz, sca_xyz]:
        if details:
            # prolly validate, then set
            set_detailed_value_remap(props)
        else:
            set_default_value_remap(props[0])


def main():
    ob = bpy.types.Object()
    tar_ob, sub_tar, tar_type = get_target(ob.cgt_props)
    if tar_type == 'ABORT':
        return
