from __future__ import annotations
import logging
from typing import Optional, List
import mathutils
import bpy


def add_empties(data: dict, size: float, prefix: str = "", suffix: str = "") -> List[bpy.types.Object]:
    return [add_empty(size=size, name=suffix + value + prefix) for key, value in data.items()]


def add_empty(size, name, display='ARROWS') -> bpy.types.Object:
    ob = get_object_by_name(name)
    if ob is not None:
        return ob

    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = size
    obj.empty_display_type = display
    return obj


def get_object_by_name(name) -> Optional[bpy.types.Object]:
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    return None


def purge_orphan_data():
    # remove all orphan data blocks
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    # remove all orphan armatures
    for armature in bpy.data.armatures:
        if armature.users == 0:
            bpy.data.armatures.remove(armature)


def get_pbone_worldspace(
        pose_bone: bpy.types.PoseBone,
        rig: bpy.types.Object) -> List[float]:
    """ Gets world space position of a pose bone. """

    world_space = rig.convert_space(
        pose_bone=pose_bone,
        matrix=pose_bone.matrix,
        from_space='POSE',
        to_space='WORLD'
    )

    return world_space


def set_pbone_worldspace(
        pose_bone: bpy.types.PoseBone,
        rig: bpy.types.Object, position: mathutils.Vector) -> None:
    """ Sets a pose bone to target world space position. """

    world_space = get_pbone_worldspace(pose_bone, rig)
    world_space.translation = position
    pose_bone.matrix = rig.convert_space(pose_bone=pose_bone,
                                         matrix=world_space,
                                         from_space='WORLD',
                                         to_space='POSE')


def set_mode(mode: str = None) -> bool:
    """ MODES: 'EDIT', 'OBJECT', 'POSE' """
    if mode is None:
        raise KeyError

    if bpy.context.mode == mode:
        return True
    try:
        bpy.ops.object.mode_set(mode=mode, toggle=False)
        return True

    except RuntimeError:
        logging.error("RuntimeError: Operator bpy.ops.object.mode_set.poll() Context missing active object")
        return False


def user_pref():
    return bpy.context.scene.m_cgtinker_mediapipe
