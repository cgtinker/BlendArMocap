import bpy
from bpy.props import PointerProperty
from interface import Properties, Operators, Panels
from management import detection_operator
from bpy.utils import register_class


import importlib
importlib.reload(Operators)
importlib.reload(Panels)
importlib.reload(Properties)
importlib.reload(detection_operator)

classes = (
    Properties.MyProperties,

    Operators.UI_detection_button,
    Operators.UI_transfer_anim_button,
    detection_operator.DetectionModalOperator,

    Panels.UI_PT_main_panel,
)


def register():
    for m_class in classes:
        print(m_class)
        register_class(m_class)
    print("attempt to register pointer")
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for m_class in reversed(classes):
        print(m_class)
        unregister_class(m_class)
    del bpy.types.Scene.m_cgtinker_mediapipe
