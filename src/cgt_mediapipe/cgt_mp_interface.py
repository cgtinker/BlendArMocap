import bpy
import logging
from bpy.types import Panel

from . import cgt_dependencies
from ..cgt_core.cgt_interface import cgt_core_panel


class UI_MP_Properties(bpy.types.PropertyGroup):
    button_start_detection: bpy.props.StringProperty(
        name="",
        description="Detects features and record results in stored in the cgt_driver collection.",
        default="Start Detection"
    )

    detection_input_type: bpy.props.EnumProperty(
        name="Type",
        description="Select input type.",
        items=(
            ("stream", "Webcam", ""),
            ("movie", "Movie", ""),
        )
    )

    enum_detection_type: bpy.props.EnumProperty(
        name="Target",
        description="Select detection type tracking.",
        items=(
            ("HAND", "Hands", ""),
            ("FACE", "Face", ""),
            ("POSE", "Pose", ""),
            ("HOLISTIC", "Holistic", ""),
        )
    )

    mov_data_path: bpy.props.StringProperty(
        name="File Path",
        description="File path to .mov file.",
        default='*.mov;*mp4',
        options={'HIDDEN'},
        maxlen=1024,
        subtype='FILE_PATH'
    )

    webcam_input_device: bpy.props.IntProperty(
        name="Webcam Device Slot",
        description="Select Webcam device.",
        min=0,
        max=4,
        default=0
    )

    key_frame_step: bpy.props.IntProperty(
        name="Key Step",
        description="Select keyframe step rate.",
        min=1,
        max=12,
        default=4
    )

    modal_active: bpy.props.BoolProperty(
        name="modal_active",
        description="Check if operator is running",
        default=False
    )


class UI_PT_Panel_Detection(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'} and all(cgt_dependencies.dependencies_installed)

    def movie_panel(self, user):
        layout = self.layout
        layout.row().prop(user, "mov_data_path")
        layout.row().prop(user, "enum_detection_type")
        if user.modal_active:
            layout.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection", icon='CANCEL')
        else:
            layout.row().operator("wm.cgt_feature_detection_operator", text="Detect Clip", icon='IMPORT')

    def webcam_panel(self, user):
        layout = self.layout
        layout.row().prop(user, "webcam_input_device")
        layout.row().prop(user, "key_frame_step")
        layout.row().prop(user, "enum_detection_type")
        if user.modal_active:
            layout.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection", icon='RADIOBUT_ON')
        else:
            layout.row().operator("wm.cgt_feature_detection_operator", text="Start Detection", icon='RADIOBUT_OFF')

    def draw(self, context):
        user = context.scene.cgtinker_mediapipe  # noqa
        layout = self.layout
        layout.label(text='Detect')
        layout.row().prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            self.movie_panel(user)
        else:
            self.webcam_panel(user)


class UI_PT_CGT_warning_panel(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return not all(cgt_dependencies.dependencies_installed)

    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for BlendArMocap.",
                 f"1. Open the preferences (Edit > Preferences > Add-ons).",
                 f"2. Search for the BlendArMocap add-on.",
                 f"3. Open the details section of the add-on.",
                 f"4. Click on the 'install dependencies' button."]

        for line in lines:
            layout.label(text=line)


classes = [
    UI_MP_Properties,
]

if all(cgt_dependencies.dependencies_installed):
    classes.append(UI_PT_Panel_Detection)
else:
    classes.append(UI_PT_CGT_warning_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_mediapipe = bpy.props.PointerProperty(type=UI_MP_Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
