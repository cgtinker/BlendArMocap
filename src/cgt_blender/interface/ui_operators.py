import bpy
from .. import input_manager


class UI_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to cgt_rig"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        input_manager.transfer_animation()
        return {'FINISHED'}


class WM_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer = None
    tracking_handler = None
    user = None

    @staticmethod
    def set_detection_type(detection_type):
        from ...cgt_detection import detect_hands, detect_pose, detect_face

        handlers = {
            "POSE":     detect_pose.PoseDetector,
            "HAND":     detect_hands.HandDetector,
            "FACE":     detect_face.FaceDetector,
            "HOLISTIC": ""
        }

        return handlers[detection_type]

    def execute(self, context):
        print("RUNNING MP AS TIMER DETECTION MODAL")
        self.user = context.scene.m_cgtinker_mediapipe  # noqa
        detection_type = self.user.enum_detection_type

        # hacky way to check if operator is running
        print("IS RUNNING:", self.user.detection_operator_running)
        if self.user.detection_operator_running is True:
            self.user.detection_operator_running = False
            return {'FINISHED'}
        else:
            self.user.detection_operator_running = True

        # initialize the detection model
        if self.user.detection_input_type == 'movie':
            self.init_movie_detector(detection_type)
        else:
            self.init_stream_detector(detection_type)

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def init_movie_detector(self, detection_type='HAND'):
        frame_start = bpy.context.scene.frame_start
        self.tracking_handler = self.set_detection_type(detection_type)(
            frame_start, 1, "movie")
        self.tracking_handler.input_type = 1

        camera_index = self.user.mov_data_path
        self.init_tracking_handler(camera_index)

    def init_stream_detector(self, detection_type='HAND'):
        print(f"INITIALIZING {detection_type} DETECTION")
        # frame start and key step
        frame_start = bpy.context.scene.frame_start
        key_step = self.user.key_frame_step

        # init detector
        self.tracking_handler = self.set_detection_type(detection_type)(
            frame_start, key_step, "stream")
        self.tracking_handler.input_type = 0

        camera_index = self.user.webcam_input_device
        self.init_tracking_handler(camera_index)

    def init_tracking_handler(self, cap_input):
        from ...cgt_utils import stream
        # cap dimensions
        dimensions_dict = {
            "sd": [720, 480],
            "hd": [1240, 720],
            "fhd": [1920, 1080]
        }
        dim = dimensions_dict[self.user.enum_stream_dim]

        # init tracking handler targets
        self.tracking_handler.stream = stream.Webcam(
            camera_index=cap_input,
            width=dim[0],
            height=dim[1],
            backend=int(self.user.enum_stream_type)
        )
        if not self.tracking_handler.stream.capture.isOpened():
            raise IOError("Initializing Detector failed.")

        # setup tracking handler and bridge
        self.tracking_handler.initialize_model()
        self.tracking_handler.init_bpy_bridge()
        self.tracking_handler.listener.attach(self.tracking_handler.observer)

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        if event.type == "TIMER":
            running = self.tracking_handler.image_detection()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.detection_operator_running is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        bpy.context.scene.m_cgtinker_mediapipe.detection_operator_running = False # noqa
        del self.tracking_handler
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("FINISHED DETECTION")
        return {'FINISHED'}
