import importlib

import bpy

from utils import log


class WM_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer = None
    tracking_handler = None
    user = None

    @staticmethod
    def set_detection_type(detection_type):
        from ml_detection import detect_hands, detect_pose, detect_face

        importlib.reload(detect_hands)
        importlib.reload(detect_pose)
        importlib.reload(detect_face)

        handlers = {
            "POSE": detect_pose.PoseDetector,
            "HAND": detect_hands.HandDetector,
            "FACE": detect_face.FaceDetector,
            "HOLISTIC": ""
        }

        return handlers[detection_type]

    def execute(self, context):
        log.logger.info("RUNNING MP AS TIMER DETECTION MODAL")

        # default detection type for testing while add-on is not registered
        detection_type = 'HAND'
        try:
            self.user = context.scene.m_cgtinker_mediapipe
            detection_type = self.user.enum_detection_type
        except AttributeError:
            log.logger.error("CGT USER NOT FOUND")
            self.user = None

        # initialize the detection
        self.init_detector(detection_type)

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def init_detector(self, detection_type='HAND'):
        from utils.open_cv import stream
        importlib.reload(stream)

        log.logger.info(f"INITIALIZING {detection_type} DETECTION")

        self.tracking_handler = self.set_detection_type(detection_type)()

        # default camera index if add-on is not registered
        camera_index = 0
        if self.user is not None:
            camera_index = self.user.webcam_input_device

        # init tracking handler targets
        self.tracking_handler.stream = stream.Webcam(camera_index=camera_index)
        self.tracking_handler.initialize_model()
        self.tracking_handler.init_bpy_bridge()
        self.tracking_handler.listener.attach(self.tracking_handler.observer)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def modal(self, context, event):
        if event.type == "TIMER":
            rt_event = self.tracking_handler.image_detection()
            return rt_event

        if event.type in {'RIGHTMOUSE', 'ESC', 'Q'}:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        del self.tracking_handler
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        log.logger.info("CANCELLED DETECTION")
        return {'CANCELLED'}
