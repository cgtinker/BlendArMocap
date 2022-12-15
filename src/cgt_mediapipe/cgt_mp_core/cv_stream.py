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

from __future__ import annotations
from typing import Union
import time
import cv2
import logging
import numpy as np


class Stream:
    updated: bool = None
    frame: np.ndarray = None
    input_type: int = None
    color_spaces = {
        'rgb': cv2.COLOR_BGR2RGB,
        'bgr': cv2.COLOR_RGB2BGR
    }

    def __init__(self, capture_input: Union[str, int] = None, title: str = "Stream Detection",
                 width: int = 640, height: int = 480, backend: int = 0):
        """ Generates a video stream for webcam or opens a movie file using cv2 """
        # improved backend for windows
        self.set_capture(capture_input, backend)
        time.sleep(.25)
        if not self.capture.isOpened():
            # if backend cannot open capture use random backend
            self.capture = cv2.VideoCapture(capture_input)
            time.sleep(.25)

            if not self.capture.isOpened():
                raise IOError("Cannot open webcam")
        self.set_capture_props(width, height)
        self.title = title

    def update(self):
        self.updated, frame = self.capture.read()
        self.frame = cv2.flip(frame, 1)

    def set_color_space(self, space):
        self.frame = cv2.cvtColor(self.frame, self.color_spaces[space])

    def draw(self):
        cv2.imshow(self.title, self.frame)

    def exit_stream(self):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logging.debug("ATTEMPT TO EXIT STEAM")
            return True
        else:
            return False

    def set_capture(self, capture_input, backend):
        if isinstance(capture_input, int):
            self.input_type = 0
        elif isinstance(capture_input, str):
            self.input_type = 1

        if backend == 0:
            self.capture = cv2.VideoCapture(capture_input)
        elif backend == 1:
            try:
                self.capture = cv2.VideoCapture(capture_input, cv2.CAP_DSHOW)
            except EOFError:
                self.capture = cv2.VideoCapture(capture_input)

    def set_capture_props(self, width, height):
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def __del__(self):
        logging.debug("DEL STREAM")
        self.capture.release()
        cv2.destroyAllWindows()


def main():
    stream = Stream()
    while stream.capture.isOpened():
        stream.update()
        stream.set_color_space('rgb')
        stream.set_color_space('bgr')
        stream.draw()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    del stream


if __name__ == "__main__":
    main()
