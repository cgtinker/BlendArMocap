import bpy

from .. import m_CONST
from ..blender.rig import rigify_hands, rigify_face, rigify_pose, rig_pose
from ..blender.utils import objects


def transfer_animation():
    col_mapping = {
        m_CONST.COLLECTIONS.hands: rigify_hands.RigifyHands,
        m_CONST.COLLECTIONS.face: rigify_face.RigifyFace,
        m_CONST.COLLECTIONS.pose: rig_pose.RigPose
        # m_CONST.COLLECTIONS.pose.value: rigify_pose.RigifyPose
    }

    user = bpy.context.scene.m_cgtinker_mediapipe

    selected_driver_collection = user.selected_driver_collection
    selected_armature = user.selected_rig

    print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

    driver_collections = objects.get_child_collections(selected_driver_collection)
    for col in driver_collections:
        armature = objects.get_armature(selected_armature)
        driver_objects = objects.get_objects_from_collection(col)
        col_mapping[col](armature, driver_objects)


def get_keyframe_step():
    try:
        user = bpy.context.scene.m_cgtinker_mediapipe
        key_step = user.key_frame_step
    except AttributeError:
        return 4
    return key_step


def get_frame_start():
    frame = objects.get_frame_start()
    return frame
