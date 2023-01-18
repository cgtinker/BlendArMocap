from __future__ import annotations

from typing import Tuple, Any, Optional, List
import bpy
import numpy as np
from ...cgt_core.cgt_calculators_nodes import cgt_math
from .. import cgt_tf_object_properties
from . import tf_check_object_properties, tf_reflect_object_properties


# driver_prop_cls_dict = None
def get_properties_from_object(obj: bpy.types.Object) -> tf_reflect_object_properties.RuntimeClass():
    """ Get properties from object as Runtime Class to not modify values in Blender by accident. """
    # global driver_prop_cls_dict
    # if driver_prop_cls_dict is None:
    #     driver_prop_cls_dict = object_prop_reflection.copy_ptr_prop_cls(object_prop_reflection.cls_type_dict)

    properties = tf_reflect_object_properties.get_object_attributes(
        # driver_prop_cls_dict["OBJECT_PGT_CGT_TransferProperties"],
        cgt_tf_object_properties.TransferPropertiesProto,
        obj.cgt_props,
        tf_reflect_object_properties.RuntimeClass()
    )

    return properties


def get_constraint_props(c: bpy.types.Constraint):
    pool = {'target', 'type', 'subtarget', 'is_valid', 'active', 'bl_rna', 'error_location', 'error_rotation',
            'head_tail', 'is_proxy_local', 'mute', 'rna_type', 'show_expanded', 'use_bbone_shape',
            'is_override_data'}
    props = {key: getattr(c, key, None) for key in dir(c) if key not in pool and not key.startswith('_')}
    return props


def get_target(tar_props: cgt_tf_object_properties.OBJECT_PGT_CGT_TransferTarget) -> Tuple[Optional[bpy.types.Object], Optional[Any], str]:
    """ Get target property and set appropriate Pointers. """
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
    assert RuntimeError, f'Type not defined. \n{tar_props}'


def get_value_by_distance_properties(cgt_props: cgt_tf_object_properties.OBJECT_PGT_CGT_TransferProperties):
    # todo: unpacking? improve check (less harsh one?)
    cgt_props = tf_check_object_properties.check_distance_mapping_object_props(cgt_props)
    return cgt_props


def get_remapping_properties(cgt_props: cgt_tf_object_properties.OBJECT_PGT_CGT_TransferProperties) -> List[List[
    cgt_tf_object_properties.OBJECT_PGT_CGT_ValueMapping]]:
    """ Validates, updates and returns remapping properties. """
    loc_xyz = [cgt_props.loc_details, [cgt_props.use_loc_x, cgt_props.use_loc_y, cgt_props.use_loc_z]]
    rot_xyz = [cgt_props.rot_details, [cgt_props.use_rot_x, cgt_props.use_rot_y, cgt_props.use_rot_z]]
    sca_xyz = [cgt_props.sca_details, [cgt_props.use_sca_x, cgt_props.use_sca_y, cgt_props.use_sca_z]]

    updated_props = []
    for details, props in [loc_xyz, rot_xyz, sca_xyz]:
        if details:
            props = tf_check_object_properties.check_value_mapping_detail_props(props)
        else:
            props = tf_check_object_properties.check_value_mapping_generic_props(props)
        updated_props.append(props)

    return updated_props


def get_distance(cur_props):
    """ Returns 'remap by' dist either from bones or the bone len... """
    if cur_props.by_obj.target is None or cur_props.by_obj.target_bone in ["NONE", None]:
        return None

    armature = cur_props.by_obj.target
    m_dist = None

    if cur_props.by_obj.target_type == 'BONE_LEN':
        m_dist = armature.pose.bones[cur_props.by_obj.target_bone].length

    elif cur_props.by_obj.target_type == 'BONE_DIST':
        assert cur_props.by_obj.target_bone is not None and cur_props.by_obj.other_bone is not None

        if cur_props.by_obj.target_bone_type == 'HEAD':
            v1 = armature.pose.bones[cur_props.by_obj.target_bone].head
        elif cur_props.by_obj.target_bone_type == 'TAIL':
            v1 = armature.pose.bones[cur_props.by_obj.target_bone].tail
        elif cur_props.by_obj.target_bone_type == 'LOCATION':
            v1 = armature.pose.bones[cur_props.by_obj.target_bone].location

        if cur_props.by_obj.other_bone_type == 'HEAD':
            v2 = armature.pose.bones[cur_props.by_obj.other_bone].head
        elif cur_props.by_obj.other_bone_type == 'TAIL':
            v2 = armature.pose.bones[cur_props.by_obj.other_bone].tail
        elif cur_props.by_obj.other_bone_type == 'LOCATION':
            v2 = armature.pose.bones[cur_props.by_obj.other_bone].location

        m_dist = cgt_math.get_vector_distance(np.array(v1), np.array(v2))
    return m_dist


