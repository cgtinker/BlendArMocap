from __future__ import annotations
from typing import Union, Tuple
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
    dim: Tuple[int, int]
    is_movie: bool = False
    frame_configured: bool = False

    def __init__(self, capture_input: Union[str, int], title: str = "Stream Detection",
                 width: int = 640, height: int = 480, backend: int = 0):
        """ Generates a video stream for webcam or opens a movie file using cv2 """
        self.set_capture(capture_input, backend)

        self.dim = (width, height)
        self.frame_configured = False
        if isinstance(capture_input, str):
            self.is_movie = True
        self.set_capture_props(width, height)

        time.sleep(.25)
        if not self.capture.isOpened():
            # if backend cannot open capture use random backend
            self.capture = cv2.VideoCapture(capture_input)
            time.sleep(.25)

            if not self.capture.isOpened():
                raise IOError("Cannot open webcam")
        self.title = title

    def update(self):
        self.updated, frame = self.capture.read()
        self.frame = cv2.flip(frame, 1)

    def set_color_space(self, space):
        self.frame = cv2.cvtColor(self.frame, self.color_spaces[space])

    def resize_movie_frame(self):
        if not self.frame_configured:
            (h, w) = self.frame.shape[:2]
            (tar_w, tar_h) = self.dim

            if h < w:   # landscape
                aspect = tar_w / float(w)
                self.dim = (tar_w, int(h*aspect))
            elif h > w:     # portrait
                aspect = tar_h / float(h)
                self.dim = (int(w*aspect), tar_h)
            else:
                self.dim = (tar_w, tar_w)

            self.frame_configured = True

        return cv2.resize(self.frame, self.dim, interpolation=cv2.INTER_AREA)

    def draw(self):
        f = self.frame
        if self.is_movie:
            f = self.resize_movie_frame()
        cv2.imshow(self.title, f)

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
    stream = Stream(0)
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
