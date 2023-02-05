import mediapipe as mp
from mediapipe.framework.formats import classification_pb2

from .mp_detector_node import DetectorNode
from . import cv_stream
from ...cgt_core.cgt_utils import cgt_timers


class HandDetector(DetectorNode):
    def __init__(self, stream, hand_model_complexity: int = 1, min_detection_confidence: float = .7):
        DetectorNode.__init__(self, stream)
        self.solution = mp.solutions.hands
        self.hand_model_complexity = hand_model_complexity
        self.min_detection_confidence = min_detection_confidence

    # https://google.github.io/mediapipe/solutions/hands#python-solution-api
    def update(self, data, frame):
        with self.solution.Hands(
                static_image_mode=True,
                max_num_hands=2,
                model_complexity=self.hand_model_complexity,
                min_detection_confidence=self.min_detection_confidence) as mp_lib:
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
    import logging
    from ...cgt_core.cgt_calculators_nodes import mp_calc_hand_rot
    from ...cgt_core.cgt_patterns import cgt_nodes
    logging.getLogger().setLevel(logging.DEBUG)

    chain = cgt_nodes.NodeChain()

    # Get detector and premade chain
    detector = HandDetector(cv_stream.Stream(0))
    calc = mp_calc_hand_rot.HandRotationCalculator()

    chain.append(detector)
    chain.append(calc)

    frame, data = 0, []
    for _ in range(50):
        frame += 1
        data, frame = chain.update(data, frame)
    del detector
# endregion
