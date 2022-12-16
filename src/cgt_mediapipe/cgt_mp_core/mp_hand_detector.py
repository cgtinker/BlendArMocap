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

import mediapipe as mp
from mediapipe.framework.formats import classification_pb2

from .mp_detector_node import DetectorNode
from . import cv_stream
from ...cgt_core.cgt_utils import cgt_timers


class HandDetector(DetectorNode):
    def __init__(self, *args, **kwargs):
        DetectorNode.__init__(self, *args, **kwargs)
        self.solution = mp.solutions.hands

    # https://google.github.io/mediapipe/solutions/hands#python-solution-api
    def update(self, data, frame):
        with self.solution.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib), frame

    @staticmethod
    def separate_hands(hand_data):
        left_hand = [data[0] for data in hand_data if data[1][1] is False]
        right_hand = [data[0] for data in hand_data if data[1][1] is True]
        return left_hand, right_hand

    @staticmethod
    def cvt_hand_orientation(orientation: classification_pb2):
        if not orientation:
            return None

        return [[idx, "Right" in str(o)] for idx, o in enumerate(orientation)]

    def empty_data(self):
        return [[], []]

    def detected_data(self, mp_res):
        data = [self.cvt2landmark_array(hand) for hand in mp_res.multi_hand_world_landmarks]
        left_hand_data, right_hand_data = self.separate_hands(
            list(zip(data, self.cvt_hand_orientation(mp_res.multi_handedness))))
        return [left_hand_data, right_hand_data]

    def contains_features(self, mp_res):
        if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, self.solution.HAND_CONNECTIONS)


if __name__ == '__main__':
    from ...cgt_core.cgt_calculators_nodes import calc_hand_rot

    detector = HandDetector(cv_stream.Stream(0))
    calc = calc_hand_rot.HandRotationCalculator()
    frame = 0
    for _ in range(50):
        frame += 1
        data, frame = detector.update(None, frame)
        data, frame = calc.update(data, frame)
        print(data)
    del detector
# endregion
