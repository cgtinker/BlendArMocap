import bpy
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty
from bpy.types import PropertyGroup


class CgtProperties(PropertyGroup):
    # region USER INTERFACE
    # region DETECTION
    button_start_detection: StringProperty(
        name="",
        description="Detects features and record results in stored in the cgt_driver collection.",
        default="Start Detection"
    )

    detection_operator_running: BoolProperty(
        name="detection operator bool",
        description="helper bool to en- and disable detection operator",
        default=False
    )

    detection_input_type: EnumProperty(
        name="Type",
        description="Select detection type for motion tracking.",
        items=(
            ("stream", "Stream", ""),
            ("movie", "Movie", ""),
        )
    )

    # region WEBCAM
    webcam_input_device: IntProperty(
        name="Webcam Device Slot",
        description="Select Webcam device.",
        min=0,
        max=4,
        default=0
    )

    key_frame_step: IntProperty(
        name="Key Step",
        description="Select keyframe step rate.",
        min=1,
        max=12,
        default=4
    )
    # endregion

    # region MOVIE
    data_path: StringProperty(
        name="File Path",
        description="File path to .mov file.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    # endregion
    # endregion

    # region TRANSFER
    button_transfer_animation: StringProperty(
        name="",
        description="Armature as target for detected results.",
        default="Transfer Animation"
    )

    experimental_feature_bool: BoolProperty(
        name="Experimental Leg Transfer",
        description="Experimental feature to transfer legs when transferring pose data",
        default=False
    )

    def armature_poll(self, object):
        return object.type == 'ARMATURE'

    selected_rig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        description="Select an armature for animation transfer.",
        name="Armature",
        poll=armature_poll)

    selected_driver_collection: StringProperty(
        name="",
        description="Select a collection of Divers.",
        default="Drivers"
    )
    # endregion

    # region SELECTION
    # ("HOLISTIC", "Holistic", ""),
    enum_detection_type: EnumProperty(
        name="Target",
        description="Select detection type for motion tracking.",
        items=(
            ("HAND", "Hands", ""),
            ("FACE", "Face", ""),
            ("POSE", "Pose", ""),
        )
    )
    # endregion
    # endregion

    # region PREFERENCES
    pvb: BoolProperty(
        name="pvb",
        description="subcontrol",
        default=False
    )

    enum_stream_dim: EnumProperty(
        name="Stream Dimensions",
        description="Dimensions for video Stream input.",
        items=(
            ("sd", "720x480 - recommended", ""),
            ("hd", "1240x720 - experimental", ""),
            ("fhd", "1920x1080 - experimental", ""),
        )
    )

    enum_stream_type: EnumProperty(
        name="Stream Backend",
        description="Sets Stream backend.",
        items=(
            ("0", "automatic", ""),
            ("1", "capdshow", "")
        )
    )
    # endregion


pvb = False


def get_user():
    return bpy.context.scene.m_cgtinker_mediapipe
