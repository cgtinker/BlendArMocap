import bpy

from ml_detection.methods import ml_hands, helper
from utils import log
from utils.open_cv import stream
import time


class DetectionModalOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.feature_detection_modal"
    bl_label = "Detection Modal"

    # detection
    observer, listener, _timer = None, None, None
    tracking_handler = None
    solution_type, solution_target = None, None
    drawing_utils, drawing_style, stream = None, None, None

    time_step = 4
    frame = 0

    def execute(self, context):
        log.logger.info("RUNNING MP AS TIMER DETECTION MODAL")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        self.tracking_handler = ml_hands.HandDetectionBridge()
        self.stream = stream.Webcam()
        self.observer, self.listener = self.tracking_handler.initialize_bridge()
        self.solution_type, self.solution_target = self.tracking_handler.initialize_model()
        self.drawing_utils, self.drawing_style = self.tracking_handler.get_drawing_solutions()
        self.listener.attach(self.observer)
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def modal(self, context, event):
        if event.type == "TIMER":
            self.run_detection()
            return {'PASS_THROUGH'}

        if event.type in {'ESC', 'Q'}:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def run_detection(self):
        start = time.time()
        # TODO: FIX WITH
        with self.solution_target(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            if not self.stream_updated():
                return {'PASS_THROUGH'}

            mp_res = helper.detect_features(mp_lib, self.stream)
            if not self.tracking_handler.contains_features(mp_res):
                self.stream.draw()
                return {'PASS_THROUGH'}

            self.listener.data = self.tracking_handler.process_detection_result(mp_res)
            self.update_listeners()
            self.tracking_handler.draw_result(self.stream, mp_res, self.drawing_utils, self.solution_type)
            self.stream.draw()
            log.logger.debug(start - time.time())
            return {'PASS_THROUGH'}

    def stream_updated(self):
        self.stream.update()
        if not self.stream.updated:
            log.logger.debug("Ignoring empty camera frame")
            return False
        return True

    def update_listeners(self):
        self.frame += self.time_step
        self.listener.frame = self.frame
        self.listener.notify()

    def cancel(self, context):
        self.listener.detach(self.observer)
        del self.observer
        del self.listener
        del self.stream
        del self.tracking_handler

        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        log.logger.info("CANCELLED")
        return {'CANCELLED'}
