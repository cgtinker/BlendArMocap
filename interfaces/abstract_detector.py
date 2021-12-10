from abc import ABC, abstractmethod
from utils import log
from ml_detection.methods import helper


class RealtimeDetector(ABC):
    stream = None
    observer, listener, _timer = None, None, None
    solution_type, solution_target = None, None
    drawing_utils, drawing_style, = None, None

    time_step = 4
    frame = 0

    @abstractmethod
    def image_detection(self):
        pass

    @abstractmethod
    def init_bpy_bridge(self):
        pass

    @abstractmethod
    def initialize_model(self):
        pass

    @abstractmethod
    def process_detection_result(self, mp_res):
        pass

    @abstractmethod
    def contains_features(self, mp_res):
        pass

    @abstractmethod
    def draw_result(self, s, mp_res, mp_drawings, mp_hands):
        pass

    def exec_img_detection(self, mp_lib):
        if not self.stream_updated():
            return {'PASS_THROUGH'}

        mp_res = helper.detect_features(mp_lib, self.stream)
        if not self.contains_features(mp_res):
            self.stream.draw()
            if self.stream.exit_stream():
                return {'CANCELLED'}
            return {'PASS_THROUGH'}

        self.listener.data = self.process_detection_result(mp_res)
        self.update_listeners()
        self.draw_result(self.stream, mp_res, self.drawing_utils, self.solution_type)
        self.stream.draw()

        if self.stream.exit_stream():
            return {'CANCELLED'}
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

    def __del__(self):
        self.listener.detach(self.observer)
        del self.observer
        del self.listener
        del self.stream
