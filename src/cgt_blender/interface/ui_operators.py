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
from pathlib import Path
from ..utils import objects
from ...cgt_naming import COLLECTIONS


class UI_CGT_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to cgt_rig"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        from ..cgt_rig import rigify_pose, rigify_face, rigify_fingers

        col_mapping = {
            COLLECTIONS.hands: rigify_fingers.RigifyHands,
            COLLECTIONS.face:  rigify_face.RigifyFace,
            COLLECTIONS.pose:  rigify_pose.RigifyPose
        }

        user = bpy.context.scene.m_cgtinker_mediapipe

        selected_driver_collection = user.selected_driver_collection
        selected_armature = user.selected_rig.name_full

        print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

        driver_collections = objects.get_child_collections(selected_driver_collection)
        for col in driver_collections:
            armature = objects.get_armature(selected_armature)
            driver_objects = objects.get_objects_from_collection(col)
            col_mapping[col](armature, driver_objects)

        # input_manager.transfer_animation()
        return {'FINISHED'}


class UI_CGT_toggle_drivers_button(bpy.types.Operator):
    bl_label = "Toggle Drivers"
    bl_idname = "button.cgt_toggle_drivers_button"
    bl_description = "Toggle drivers to improve performance while motion capturing"
    # TODO: IMPLEMENT PROPER WAY TO TOGGLE

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        user = bpy.context.scene.m_cgtinker_mediapipe  # noqa
        user.toggle_drivers_bool = not user.toggle_drivers_bool
        print("toggled", user.toggle_drivers_bool)

        driver_collections = objects.get_child_collections('CGT_DRIVERS')
        objs = objects.get_objects_from_collection('CGT_DRIVERS')
        print(objs)
        return {'FINISHED'}


class WM_CGT_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer = None
    detection_handler = None
    user = None

    def execute(self, context):
        """ Runs movie or stream detection depending on user input. """
        self.user = context.scene.m_cgtinker_mediapipe  # noqa

        # hacky way to check if operator is running
        if self.user.detection_operator_running is True:
            self.user.detection_operator_running = False
            return {'FINISHED'}
        else:
            self.user.detection_operator_running = True

        # create a detection handler
        from ...main import DetectionHandler
        detection_type = self.user.enum_detection_type
        self.detection_handler = DetectionHandler(detection_type, "BPY")

        # initialize detector using user inputs
        frame_start = bpy.context.scene.frame_start
        if self.user.detection_input_type == 'movie':
            mov_path = bpy.path.abspath(self.user.mov_data_path)
            print("Path to mov:", mov_path)
            if not Path(mov_path).is_file():
                print("GIVEN PATH IS NOT VALID")
                self.user.detection_operator_running = False
                return {'FINISHED'}
            self.detection_handler.init_detector(str(mov_path), "sd", 0, frame_start, 1, 1)
        else:
            camera_index = self.user.webcam_input_device
            dimensions = self.user.enum_stream_dim
            backend = int(self.user.enum_stream_type)
            key_step = self.user.key_frame_step
            self.detection_handler.init_detector(camera_index, dimensions, backend, frame_start, key_step, 0)

        # initialize the bridge from the detector to blender
        self.detection_handler.init_bridge()

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        print(f"RUNNING {detection_type} DETECTION AS MODAL")
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            running = self.detection_handler.detector.image_detection()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.detection_operator_running is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear the handlers. """
        bpy.context.scene.m_cgtinker_mediapipe.detection_operator_running = False # noqa
        del self.detection_handler
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("FINISHED DETECTION")
        return {'FINISHED'}
