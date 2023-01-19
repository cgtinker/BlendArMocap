import bpy

from . import cgt_dependencies
from ..cgt_core.cgt_interface import cgt_core_panel


class CGT_PT_MP_Detection(cgt_core_panel.DefaultPanel, bpy.types.Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_idname="UI_PT_CGT_Detection"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'} and all(cgt_dependencies.dependencies_installed)

    def movie_panel(self, user):
        layout = self.layout
        layout.row().prop(user, "mov_data_path")
        layout.row().prop(user, "key_frame_step")
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


class CGT_PT_MP_DetectorProperties(cgt_core_panel.DefaultPanel, bpy.types.Panel):
    bl_label = "Advanced"
    bl_parent_id = "UI_PT_CGT_Detection"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        user = context.scene.cgtinker_mediapipe # noqa
        layout = self.layout

        if user.enum_detection_type == 'HAND':
            layout.row().prop(user, "hand_model_complexity")
        elif user.enum_detection_type == 'FACE':
            # layout.row().prop(user, "refine_face_landmarks")
            pass
        elif user.enum_detection_type == 'POSE':
            layout.row().prop(user, "pose_model_complexity")
        elif user.enum_detection_type == 'HOLISTIC':
            layout.row().prop(user, "holistic_model_complexity")

        layout.row().prop(user, "min_detection_confidence", slider=True)


class CGT_PT_MP_Warning(cgt_core_panel.DefaultPanel, bpy.types.Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_idname="UI_PT_CGT_Detection_Warning"

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
    CGT_PT_MP_Warning,
    CGT_PT_MP_Detection,
    CGT_PT_MP_DetectorProperties
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
