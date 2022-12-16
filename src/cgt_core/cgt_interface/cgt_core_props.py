import bpy

from bpy.props import StringProperty, PointerProperty


class CGTProperties(bpy.types.PropertyGroup):
    # region USER INTERFACE
    # region DETECTION
    button_start_detection: StringProperty(
        name="",
        description="Detects features and record results in stored in the cgt_driver collection.",
        default="Start Detection"
    )


def register():
    bpy.utils.register_class(CGTProperties)
    bpy.types.Scene.m_cgtinker_mediapipe = bpy.props.PointerProperty(type=CGTProperties)


def unregister():
    bpy.utils.unregister_class(CGTProperties)