'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty, FloatVectorProperty
from bpy.types import PropertyGroup


class CGTProperties(PropertyGroup):
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
            ("freemocap", "freemocap", ""),
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
    mov_data_path: StringProperty(
        name="File Path",
        description="File path to .mov file.",
        default='*.mov;*mp4',
        options={'HIDDEN'},
        maxlen=1024,
        subtype='FILE_PATH'
    )

    # endregion
    
    freemocap_session_path: StringProperty(
        name="Freemocap Session Path",
        description="path to `freemocap` session folder",
        default=r"C:\Users\jonma\Dropbox\FreeMoCapProject\FreeMocap_Data\sesh_2022-04-19_11_29_31_testy_westy_2",
        options={'HIDDEN'},
        maxlen=1024,
        subtype='DIR_PATH'
    )


    # endregion

    # region TRANSFER
    button_transfer_animation: StringProperty(
        name="",
        description="Armature as target for detected results.",
        default="Transfer Animation"
    )

    experimental_feature_bool: BoolProperty(
        name="Transfer Legs (Experimental)",
        description="Transfer pose legs motion to rigify rig",
        default=False
    )

    overwrite_drivers_bool: BoolProperty(
        name="Overwrite Drivers",
        description="Overwrites drivers when reimporting",
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
            ("HOLISTIC", "Holistic (Experimental)", ""),
            ("HAND", "Hands", ""),
            ("FACE", "Face", ""),
            ("POSE", "Pose", ""),            
        )
    )
    # endregion
    # endregion

    # region PREFERENCES
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

    def set_bool(self, value):
        return None

    pvb: BoolProperty(
        name="pvb",
        default=True,
        set=set_bool
    )

    transfer_type_path: StringProperty(
        name="Dir Path",
        description="Path to folder containing Hand, Pose and Face jsons.",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    # endregion

    # region REMAPPING
    toggle_drivers_bool: BoolProperty(
        name="Toggle Drivers",
        description="helper bool to en- and disable drivers",
        default=True
    )
    # endregion
def get_user():
    return bpy.context.scene.m_cgtinker_mediapipe
