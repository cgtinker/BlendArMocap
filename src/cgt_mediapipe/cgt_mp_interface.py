import bpy
import logging
from bpy.types import Panel
from ..cgt_mediapipe import dependencies

from pathlib import Path
from .cgt_mp_core import cv_stream, mp_hand_detector, mp_face_detector, mp_pose_detector, mp_holistic_detector
from ..cgt_core.cgt_interface import cgt_core_panel
from ..cgt_core.cgt_calculators_nodes import calc_face_rot, calc_pose_rot, calc_hand_rot
from ..cgt_core.cgt_patterns import cgt_nodes
from ..cgt_core import cgt_core_chains


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
            ("HOLISTIC", "Holistic (Experimental)", ""),
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


class WM_CGT_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer: bpy.types.Timer = None
    node_chain: cgt_nodes.NodeChain = None
    frame = key_step = 1
    user = None

    def get_chain(self, stream: cv_stream.Stream) -> cgt_nodes.NodeChain:
        detectors = {
            "HAND": mp_hand_detector.HandDetector,
            "FACE": mp_face_detector.FaceDetector,
            "POSE": mp_pose_detector.PoseDetector,
            "HOLISTIC": mp_holistic_detector.HolisticDetector,
        }

        calculators = {
            "HAND": cgt_core_chains.HandNodeChain,
            "FACE": cgt_core_chains.FaceNodeChain,
            "POSE": cgt_core_chains.PoseNodeChain,
            "HOLISTIC": cgt_core_chains.HolisticNodeChainGroup,
        }

        node_chain = cgt_nodes.NodeChain()
        input_node = detectors[self.user.enum_detection_type](stream)
        node_chain.append(input_node)
        node_chain.append(calculators[self.user.enum_detection_type]())

        logging.info(f"{node_chain}")
        return node_chain

    def get_stream(self):
        self.frame = bpy.context.scene.frame_current
        if self.user.detection_input_type == 'movie':
            mov_path = bpy.path.abspath(self.user.mov_data_path)
            logging.info(f"Path to mov: {mov_path}")
            if not Path(mov_path).is_file():
                self.user.modal_active = False
                logging.error(f"GIVEN PATH IS NOT VALID {mov_path}")
                return {'FINISHED'}

            stream = cv_stream.Stream(str(mov_path), "Movie Detection")

        else:
            camera_index = self.user.webcam_input_device
            self.key_step = self.user.key_frame_step
            # dimensions = self.user.enum_stream_dim
            # backend = int(self.user.enum_stream_type)
            stream = cv_stream.Stream(capture_input=camera_index, backend=0)
        return stream

    def execute(self, context):
        """ Runs movie or stream detection depending on user input. """
        self.user = context.scene.cgtinker_mediapipe  # noqa

        # don't activate if modal is running
        if self.user.modal_active is True:
            self.user.modal_active = False
            logging.info("Stopped detection as modal has been active.")
            return {'FINISHED'}
        else:
            self.user.modal_active = True

        stream = self.get_stream()
        self.node_chain = self.get_chain(stream)

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        logging.info(f"RUNNING {self.user.enum_detection_type} DETECTION AS MODAL")
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            data, _ = self.node_chain.update([], self.frame)
            self.frame += self.key_step
            if data is not None:
                return {'PASS_THROUGH'}
            else:
                logging.debug("Data is None, finish detection.")
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear the handlers. """
        self.user.modal_active = False  # noqa
        del self.node_chain
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        logging.debug("FINISHED DETECTION")
        return {'FINISHED'}


class UI_PT_Panel_Detection(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'} and dependencies.dependencies_installed:
            return True

    def draw(self, context):
        user = context.scene.cgtinker_mediapipe  # noqa
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




class UI_PT_CGT_warning_panel(cgt_core_panel.DefaultPanel, Panel):
     bl_label = "CGT_WARN"
     bl_idname = "OBJECT_PT_warning_panel"

     @classmethod
     def poll(self, context):
         return not dependencies.dependencies_installed

     def draw(self, context):
         layout = self.layout

         lines = [f"Please install the missing dependencies for BlendArMocap.",
                  f"1. Open the preferences (Edit > Preferences > Add-ons).",
                  f"2. Search for the BlendArMocap add-on.",
                  f"3. Open the details section of the add-on.",
                  f"4. Click on the 'install dependencies' button.",
                  f"   This will download and install the missing Python packages, if Blender has the required",
                  f"   permissions."]

         for line in lines:
             layout.label(text=line)


classes = [
    UI_MP_Properties,
    WM_CGT_modal_detection_operator,
    UI_PT_Panel_Detection,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_mediapipe = bpy.props.PointerProperty(type=UI_MP_Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
