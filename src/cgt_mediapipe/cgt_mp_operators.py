import bpy
from pathlib import Path
from src.cgt_core.mediapipe_processing_manager import RealtimeDataProcessingManager


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
        if self.user.modal_active is True:
            self.user.modal_active = False
            return {'FINISHED'}
        else:
            self.user.modal_active = True

        # create a detection handler
        detection_type = self.user.enum_detection_type
        self.detection_handler = RealtimeDataProcessingManager(detection_type, "BPY")

        # initialize detector using user inputs
        frame_start = bpy.context.scene.frame_start
        print(self.user.detection_input_type)
        if self.user.detection_input_type == 'movie':
            mov_path = bpy.path.abspath(self.user.mov_data_path)
            print("Path to mov:", mov_path)
            if not Path(mov_path).is_file():
                print("GIVEN PATH IS NOT VALID")
                self.user.modal_active = False
                return {'FINISHED'}
            self.detection_handler.init_detector(str(mov_path), "sd", 0, frame_start, 1, 1)

        elif self.user.detection_input_type == 'freemocap':
            self.detection_handler = RealtimeDataProcessingManager("FREEMOCAP", "BPY")
            freemocap_session_path = Path(bpy.path.abspath(self.user.freemocap_session_path)).parent
            print("Path to freemocap_session_path:", freemocap_session_path)
            if not Path(freemocap_session_path).is_dir():
                print("GIVEN PATH IS NOT VALID")
                self.user.modal_active = False
                return {'FINISHED'}
            self.detection_handler.init_detector(input_type=2)  # input_type=2 <- freemocap_session

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
            running = self.detection_handler.realtime_data_provider.update()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear the handlers. """
        bpy.context.scene.m_cgtinker_mediapipe.modal_active = False # noqa
        del self.detection_handler
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("FINISHED DETECTION")
        return {'FINISHED'}