from __future__ import annotations

import logging
from typing import List
from mediapipe import solutions
from . import cv_stream
from ...cgt_core.cgt_patterns.observer_pattern import *


class MediapipeDetector(Subject):
    stream: cv_stream.Stream = None
    solution = None

    _observers: List[Observer]

    def __init__(self, stream: cv_stream.Stream = None):
        self.stream = stream
        self.drawing_utils = solutions.drawing_utils
        self.drawing_style = solutions.drawing_styles

        self._observers = []

    def attach(self, observer: Observer) -> None:
        logging.debug(f"Observer attached to RealtimeDataProvider: {self.__class__.__name__}")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        logging.debug(f"Observer detached from RealtimeDataProvider: {self.__class__.__name__}")
        self._observers.remove(observer)

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_detection_results(self, mp_res):
        pass

    @abstractmethod
    def contains_features(self, mp_res):
        pass

    @abstractmethod
    def draw_result(self, s, mp_res, mp_drawings):
        pass

    def exec_detection(self, mp_lib):
        self.stream.update()
        updated = self.stream.updated

        if not updated and self.stream.input_type == 0:
            # ignore if an update fails while stream detection
            return True

        elif not updated and self.stream.input_type == 1:
            # stop detection if update fails while movie detection
            return False

        if self.stream.frame is None:
            # ignore frame if not available
            return True

        # detect features in frame
        self.stream.frame.flags.writeable = False
        self.stream.set_color_space('rgb')
        mp_res = mp_lib.process(self.stream.frame)
        self.stream.set_color_space('bgr')

        # proceed if contains features
        if not self.contains_features(mp_res):
            self.stream.draw()
            if self.stream.exit_stream():
                return False
            return True

        # draw results
        self.draw_result(self.stream, mp_res, self.drawing_utils)
        self.stream.draw()

        # update observers
        self.notify()

        # exit stream
        if self.stream.exit_stream():
            return False
        return True

    def notify(self):
        """ todo: attach stuff? """
        for observer in self._observers:
            observer.update(self)

    def cvt2landmark_array(self, landmark_list):
        """landmark_list: A normalized landmark list proto message to be annotated on the image."""
        return [[idx, [landmark.x, landmark.y, landmark.z]] for idx, landmark in enumerate(landmark_list.landmark)]

    def __del__(self):
        if self.stream is not None:
            del self.stream
