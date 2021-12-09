import bpy
from custom_data import cd_hand
from utils.open_cv import stream
import mediapipe as mp
from bridge import events
from utils import log
from ml_detection.stream import helper
import time


class FeatureDetectionModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.feature_detection_modal"
    bl_label = "Feature Detection Modal"

    # internals
    target = None
    observer = None
    listener = None
    stream = None
    _timer = None

    # properties
    running = False
    min_detection_confidence: float = 0.8
    min_tracking_confidence: float = 0.5

    # frame timing
    time_step = 4
    frame = 0

    @classmethod
    def poll(cls, context):
        # check if player is in object mode
        return context.mode == 'OBJECT'

    def modal(self, context, event):
        if event.type == "TIMER":
            self.detection()
            return {'PASS_THROUGH'}

        if event.type in {'ESC', 'Q'}:
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        log.logger.info("FEATURE DETECTION MODAL INVOKED")
        # start webcam
        self.stream = stream.Webcam()

        # initialize bridge
        self.target = cd_hand.Hand()
        self.observer = events.BpyHandUpdateReceiver(self.target)
        self.listener = events.UpdateListener()
        self.listener.attach(self.observer)

        # start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def detection(self):
        # data and display specs
        mp_hands = mp.solutions.hands
        mp_drawings = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        cur_t = time.time()
        with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            self.stream.update()
            if not self.stream.updated:
                # break if loading video file
                log.logger.debug("Ignoring empty camera frame")
                return {'PASS_THROUGH'}

            mp_res = helper.detect_features(mp_lib, self.stream)

            # draw stream and stop processing if no landmarks are available
            if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
                self.stream.draw()
                if self.stream.exit_stream():
                    return {'CANCELLED'}
                return {'PASS_THROUGH'}

            # send converted data to bridge
            self.listener.data = (
                [helper.cvt2landmark_array(hand) for hand in mp_res.multi_hand_landmarks],
                helper.cvt_hand_orientation(mp_res.multi_handedness)
            )
            self.frame += self.time_step
            self.listener.frame = self.frame
            self.listener.notify()

            # render
            draw_hands(self.stream, mp_res, mp_drawings, mp_hands)
            self.stream.draw()
            if self.stream.exit_stream():
                return {'CANCELLED'}
            return {'PASS_THROUGH'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        del self.stream
        self.listener.detach(self.observer)


def draw_hands(s, mp_res, mp_drawings, mp_hands):
    """Draws the landmarks and the connections on the image."""
    for hand in mp_res.multi_hand_landmarks:
        mp_drawings.draw_landmarks(s.frame, hand, mp_hands.HAND_CONNECTIONS)
