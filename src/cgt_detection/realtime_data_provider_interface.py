'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import logging
from abc import ABC, abstractmethod
from mediapipe import solutions
from ..cgt_patterns import observer_pattern


class RealtimeDataProvider(ABC):
    stream = None
    input_type = 0
    observer, listener, _timer = None, None, None
    solution = None
    drawing_utils, drawing_style, = None, None
    key_step = 4
    frame = None

    def __init__(self, frame_start: int = 0, key_step: int = 4, input_type: int = None):
        self.input_type = input_type  # stream or movie (0/1)
        self.drawing_utils = solutions.drawing_utils
        self.drawing_style = solutions.drawing_styles
        self.frame = frame_start
        self.key_step = key_step

    @abstractmethod
    def frame_detection_data(self):
        """ Run mediapipes detection on an image using the active model. """
        pass

    def init_bridge(self, observer: observer_pattern.Observer, listener: observer_pattern.Listener, ):
        """ Set up the data bridge to blender or to prints for debugging purposes. """
        self.observer = observer
        self.listener = listener
        self.listener.attach(self.observer)

    @abstractmethod
    def initialize_model(self):
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

        if not updated and self.input_type == 0:
            # ignore if an update fails while stream detection
            return True

        elif not updated and self.input_type == 1:
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

        # update listeners
        self.listener.data = self.get_detection_results(mp_res)
        self.update_listeners()

        # exit stream
        if self.stream.exit_stream():
            return False
        return True

    def update_listeners(self):
        self.frame += self.key_step
        self.listener.frame = self.frame
        self.listener.notify()

    def cvt2landmark_array(self, landmark_list):
        """landmark_list: A normalized landmark list proto message to be annotated on the image."""
        return [[idx, [landmark.x, landmark.y, landmark.z]] for idx, landmark in enumerate(landmark_list.landmark)]

    def __del__(self):
        self.listener.detach(self.observer)
        del self.observer
        del self.listener
        if self.stream is not None:
            del self.stream
