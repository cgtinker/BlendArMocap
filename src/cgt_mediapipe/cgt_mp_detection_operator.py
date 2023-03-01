import bpy
import logging

from pathlib import Path
from ..cgt_core.cgt_patterns import cgt_nodes


class WM_CGT_MP_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer: bpy.types.Timer = None
    node_chain: cgt_nodes.NodeChain = None
    frame = key_step = 1
    memo = None
    user = None

    def get_chain(self, stream) -> cgt_nodes.NodeChain:
        from ..cgt_core import cgt_core_chains
        from .cgt_mp_core import mp_hand_detector, mp_face_detector, mp_pose_detector, mp_holistic_detector

        # create new node chain
        node_chain = cgt_nodes.NodeChain()

        input_node = None
        chain_template = None

        logging.debug(f"{self.user.enum_detection_type}")
        if self.user.enum_detection_type == 'HAND':
            input_node = mp_hand_detector.HandDetector(
                stream, self.user.hand_model_complexity, self.user.min_detection_confidence
            )
            chain_template = cgt_core_chains.HandNodeChain()

        elif self.user.enum_detection_type == 'POSE':
            input_node = mp_pose_detector.PoseDetector(
                stream, self.user.pose_model_complexity, self.user.min_detection_confidence
            )
            chain_template = cgt_core_chains.PoseNodeChain()

        elif self.user.enum_detection_type == 'FACE':
            input_node = mp_face_detector.FaceDetector(
                stream, self.user.refine_face_landmarks, self.user.min_detection_confidence
            )
            chain_template = cgt_core_chains.FaceNodeChain()

        elif self.user.enum_detection_type == 'HOLISTIC':
            input_node = mp_holistic_detector.HolisticDetector(
                stream, self.user.holistic_model_complexity,
                self.user.min_detection_confidence, self.user.refine_face_landmarks
            )
            chain_template = cgt_core_chains.HolisticNodeChainGroup()

        if input_node is None or chain_template is None:
            self.report({'ERROR'}, f"Setting up nodes failed: Input: {input_node}, Chain: {chain_template}")
            return None

        node_chain.append(input_node)
        node_chain.append(chain_template)

        logging.info(f"{node_chain}")
        return node_chain

    def get_stream(self):
        from .cgt_mp_core import cv_stream
        self.key_step = self.user.key_frame_step

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
            dim = self.user.enum_stream_dim
            dimensions = {
                'sd': (720, 480),
                'hd': (1240, 720),
                'fhd': (1920, 1080)
            }
            backend = int(self.user.enum_stream_type)

            stream = cv_stream.Stream(
                capture_input=camera_index, backend=backend,
                width=dimensions[dim][0], height=dimensions[dim][1],
            )
        return stream

    def execute(self, context):
        """ Runs movie or stream detection depending on user input. """
        self.user = context.scene.cgtinker_mediapipe  # noqa

        # don't activate if modal is running
        if self.user.modal_active is True:
            self.user.modal_active = False
            self.report({'INFO'}, "Stopped detection.")
            return {'FINISHED'}
        else:
            self.user.modal_active = True

        # init stream and chain
        stream = self.get_stream()
        self.node_chain = self.get_chain(stream)
        if self.node_chain is None:
            self.user.modal_active = False
            return {'FINISHED'}

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        # memo skipped frames
        self.memo = []
        self.report({'INFO'}, f"Running {self.user.enum_detection_type} as modal.")
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    @staticmethod
    def simple_smoothing(memo, cur):
        """ Expects list with sub-lists containing [int, [float, float, float]].
        Smooths the float part of the sub-lists. """
        def smooth_by_add_divide(x, y):
            for i, *_ in enumerate(zip(x, y)):
                x[i] += y[i]
                x[i] /= 2

        def addable(x, y):
            # check if [int, [float, float float]]
            if not isinstance(x, list) or not isinstance(y, list):
                print("CATCHED NOT LIST ERR")
                return False

            if not len(x) == 2 or not len(y) == 2:
                return False

            if not len(x[1]) == 3 or not len(y[1]) == 3:
                return False

            smooth_by_add_divide(x[1], y[1])
            return True

        def smooth_memo_contents(x, y):
            # checks if addable contents, else splits into sub-arrays
            # and retries. y may get added to x, if x is empty.
            if not isinstance(y, list):
                return
            if not isinstance(x, list):
                x = y
            if len(x) == 0 and len(y) != 0:
                x += y

            for l1, l2 in zip(x, y):
                if not addable(l1, l2):
                    smooth_memo_contents(l1, l2)

        smooth_memo_contents(memo, cur)
        return memo

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER" and self.user.modal_active:
            if self.user.detection_input_type == 'movie':
                # get data
                data, _frame = self.node_chain.nodes[0].update([], self.frame)
                if data is None:
                    return self.cancel(context)

                # smooth gathered data
                self.simple_smoothing(self.memo, data)
                if self.frame % self.key_step == 0:
                    for node in self.node_chain.nodes[1:]:
                        node.update(self.memo, self.frame)
                    self.memo.clear()

                self.frame += 1
            else:
                data, _ = self.node_chain.update([], self.frame)
                if data is None:
                    return self.cancel(context)
                self.frame += self.key_step

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
    bpy.utils.register_class(WM_CGT_MP_modal_detection_operator)


def unregister():
    bpy.utils.unregister_class(WM_CGT_MP_modal_detection_operator)
