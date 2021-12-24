from abc import ABC, abstractmethod
from utils import log
from mediapipe.framework.formats import classification_pb2
from mediapipe import solutions
from time import time
from math import ceil
import bpy


class RealtimeDetector(ABC):
    stream = None
    observer, listener, _timer = None, None, None
    solution = None
    drawing_utils, drawing_style, = None, None

    start_time = 0.0
    frame_rate = 25.0
    time_step = 4
    frame = 0

    def __init__(self):
        self.drawing_utils = solutions.drawing_utils
        self.drawing_style = solutions.drawing_styles
        self.frame_rate = self.get_frame_rate()

    @staticmethod
    def get_frame_rate():
        try:
            fps = bpy.context.scene.m_cgtinker_mediapipe.enum_fps
            fps = int(fps)
        except AttributeError:
            fps = 25
        return fps

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
    def draw_result(self, s, mp_res, mp_drawings):
        pass

    def exec_detection(self, mp_lib):
        if not self.stream_updated():
            return {'PASS_THROUGH'}
        self.start_time = time()

        # detect features in frame
        self.stream.frame.flags.writeable = False
        self.stream.set_color_space('rgb')
        mp_res = mp_lib.process(self.stream.frame)
        self.stream.set_color_space('bgr')

        # proceed if contains features
        if not self.contains_features(mp_res):
            self.stream.draw()
            if self.stream.exit_stream():
                return {'CANCELLED'}
            return {'PASS_THROUGH'}

        # draw results
        self.draw_result(self.stream, mp_res, self.drawing_utils)
        self.stream.draw()

        # update listeners
        self.listener.data = self.process_detection_result(mp_res)
        self.update_listeners()

        # exit stream
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
        self.frame += ceil((time() - self.start_time) * self.frame_rate)
        # self.frame += self.time_step
        self.listener.frame = self.frame
        self.listener.notify()

    def cvt2landmark_array(self, landmark_list):
        """landmark_list: A normalized landmark list proto message to be annotated on the image."""
        return [[idx, [landmark.x, landmark.y, landmark.z]] for idx, landmark in enumerate(landmark_list.landmark)]

    def cvt_hand_orientation(self, orientation: classification_pb2):
        if not orientation:
            return None

        return [[idx, "Right" in str(o)] for idx, o in enumerate(orientation)]

    def __del__(self):
        self.listener.detach(self.observer)
        del self.observer
        del self.listener
        del self.stream
