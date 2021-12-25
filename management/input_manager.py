import bpy
from blender import objects
from blender.rig import rigify_hands
import importlib

importlib.reload(rigify_hands)


def start_detection():
    bpy.ops.wm.feature_detection_modal('EXEC_DEFAULT')


def transfer_animation():
    col_mapping = {
        "cgt_hands": rigify_hands.RigifyHands,
        "cgt_face": rigify_hands.RigifyHands,
        "cgt_pose": rigify_hands.RigifyHands
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
    user = bpy.context.scene.m_cgtinker_mediapipe
    key_step = user.key_frame_step
    return key_step


def get_frame_start():
    frame = objects.get_frame_start()
    return frame
