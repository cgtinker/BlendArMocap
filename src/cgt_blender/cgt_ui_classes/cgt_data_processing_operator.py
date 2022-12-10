import logging
import bpy
from bpy.types import Operator


class WM_CGT_modal_data_processing_operator(Operator):
    _timer = None
    user, processing_manager = None, None

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def execute(self, context):
        self.user = bpy.context.scene.m_cgtinker_mediapipe
        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        logging.debug(f'Start running modal operator {self.__class__.__name__}')
        return {'RUNNING_MODAL'}

    def toggle_modal(self) -> bool:
        """ Check if already a modal is running.
            If, it stops running, else, it starts. """
        user = bpy.context.scene.m_cgtinker_mediapipe # noqa
        # hacky way to check if operator is running
        if user.modal_active is True:
            user.modal_active = False
            return False
        user.modal_active = True
        return True

    def setup_processing_manager(self, target: str, bridge_type: str):
        """ Setup processing manager - capsules dependency chain. """
        from ...cgt_detection.main import RealtimeDataProcessingManager
        self.processing_manager = RealtimeDataProcessingManager(target, bridge_type)

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            running = self.processing_manager.realtime_data_provider.frame_detection_data()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        user = bpy.context.scene.m_cgtinker_mediapipe # noqa
        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear time and remove manager. """
        bpy.context.scene.m_cgtinker_mediapipe.modal_active = False # noqa
        del self.processing_manager
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        logging.debug("FINISHED DETECTION")
        return {'FINISHED'}
