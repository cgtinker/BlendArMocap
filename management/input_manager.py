import bpy
from blender.utils import objects
from blender.rig import rigify_hands, rigify_face
from blender.rig import rigify_pose
import importlib

importlib.reload(rigify_hands)
importlib.reload(rigify_pose)
importlib.reload(rigify_face)


def transfer_animation():
    col_mapping = {
        "cgt_hands": rigify_hands.RigifyHands,
        "cgt_face": rigify_face.RigifyFace,
        "cgt_pose": rigify_pose.RigifyPose
    }

    user = bpy.context.scene.m_cgtinker_mediapipe

    selected_driver_collection = user.selected_driver_collection
    selected_armature = user.selected_rig

    driver_collections = objects.get_child_collections(selected_driver_collection)
    for col in driver_collections:
        try:
            armature = objects.get_armature(selected_armature)
            driver_objects = objects.get_objects_from_collection(col)
            col_mapping[col](armature, driver_objects)
        except KeyError:
            print("Collection mapping failed:", col)


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
