import logging
import bpy
from pathlib import Path
from bpy.types import Operator


class WM_Load_Freemocap_Operator(Operator):
    bl_label = "Load Freemocap Session"
    bl_idname = "wm.cgt_load_freemocap_operator"
    bl_description = "Load Freemocap Session data from directory."

    user = freemocap_session_path = _timer = processing_manager = None

    def execute(self, context):
        """ Loads Freemocap data from session directory. """
        self.user = bpy.context.scene.m_cgtinker_mediapipe
        if not self.toggle_modal():
            return {'FINISHED'}

        if not self.is_valid_session_directory(self.user.freemocap_session_path):
            return {'FINISHED'}

        from ..cgt_detection.main import RealtimeDataProcessingManager
        self.processing_manager = RealtimeDataProcessingManager("FREEMOCAP", "BPY")
        self.processing_manager.init_detector(input_type=2)
        self.processing_manager.init_bridge()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        logging.debug(f'Start running modal operator {self.__class__.__name__}')
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            running = self.processing_manager.realtime_data_provider.frame_detection_data()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear time and remove manager. """
        self.user.modal_active = False
        del self.processing_manager
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        logging.debug("FINISHED DETECTION")
        return {'FINISHED'}

    def is_valid_session_directory(self, path):
        """ TODO: Improve directory validation. """
        self.freemocap_session_path = Path(bpy.path.abspath(path)).parent
        if not Path(self.freemocap_session_path).is_dir():
            self.user.modal_active = False
            logging.error(f"Given path doesn't point to a directory containing freemocap session data."
                          f"\n{self.freemocap_session_path}")
            return False
        logging.debug(f"Path to freemocap session: {self.freemocap_session_path}")
        return True

    def toggle_modal(self) -> bool:
        """ Check if already a modal is running.
            If, it stops running, else, it starts. """
        # hacky way to check if operator is running
        if self.user.modal_active is True:
            self.user.modal_active = False
            return False
        self.user.modal_active = True
        return True
