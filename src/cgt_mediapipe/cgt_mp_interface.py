import bpy
from bpy.types import Panel
from ..cgt_core.cgt_interface import cgt_main_panel
from ..cgt_mediapipe import dependencies


class UI_PT_Panel_Detection(cgt_main_panel.DefaultPanel, Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'} and dependencies.dependencies_installed:
            return True

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box = self.layout.box()
        box.label(text='Detect')
        box.row().prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            box.row().prop(user, "mov_data_path")
        else:
            box.row().prop(user, "webcam_input_device")
            box.row().prop(user, "key_frame_step")

        box.row().prop(user, "enum_detection_type")
        if user.modal_active:
            box.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection")
        else:
            box.row().operator("wm.cgt_feature_detection_operator", text="Start Detection")


classes = [
    UI_PT_Panel_Detection
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
