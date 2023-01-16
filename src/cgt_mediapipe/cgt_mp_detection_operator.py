'''
Copyright (C) Denys Hsu, cgtinker.com, hello@cgtinker.com

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
import logging

from pathlib import Path

from ..cgt_core.cgt_patterns import cgt_nodes
from ..cgt_core import cgt_core_chains
from .cgt_mp_core import cv_stream, mp_hand_detector, mp_face_detector, mp_pose_detector, mp_holistic_detector


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
            "HAND":     mp_hand_detector.HandDetector,
            "FACE":     mp_face_detector.FaceDetector,
            "POSE":     mp_pose_detector.PoseDetector,
            "HOLISTIC": mp_holistic_detector.HolisticDetector,
        }

        calculators = {
            "HAND":     cgt_core_chains.HandNodeChain,
            "FACE":     cgt_core_chains.FaceNodeChain,
            "POSE":     cgt_core_chains.PoseNodeChain,
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
            if data is None:
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


def register():
    bpy.utils.register_class(WM_CGT_modal_detection_operator)


def unregister():
    bpy.utils.unregister_class(WM_CGT_modal_detection_operator)
