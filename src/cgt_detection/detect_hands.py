import mediapipe as mp

from . import detector_interface
from ..cgt_bridge import bpy_hand_bridge
from ..cgt_processing import hand_processing
from ..cgt_patterns import events
from ..cgt_utils import stream


class HandDetector(detector_interface.RealtimeDetector):
    # https://google.github.io/mediapipe/solutions/hands#python-solution-api
    def image_detection(self):
        with self.solution.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.Hands(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                static_image_mode=False,
                max_num_hands=2
        ) as mp_lib:
            while self.stream.capture.isOpened():
                return self.exec_detection(mp_lib)

    def initialize_model(self):
        self.solution = mp.solutions.hands

    def init_bpy_bridge(self):
        target = hand_processing.HandProcessor(bpy_hand_bridge.BpyHandBridge)
        self.observer = events.BpyUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_debug_logs(self):
        target = hand_processing.HandProcessor()
        # self.observer = events.DriverDebug(target)
        self.observer = events.PrintRawDataUpdate()
        self.listener = events.UpdateListener()

    def seperate_hands(self, hand_data):
        left_hand = [data[0] for data in hand_data if data[1][1] is False]
        right_hand = [data[0] for data in hand_data if data[1][1] is True]
        return left_hand, right_hand

    def get_detection_results(self, mp_res):
        data = [self.cvt2landmark_array(hand) for hand in mp_res.multi_hand_world_landmarks]
        # multi_hand_world_landmarks // multi_hand_landmarks
        left_hand_data, right_hand_data = self.seperate_hands(
            list(zip(data, self.cvt_hand_orientation(mp_res.multi_handedness))))
        return left_hand_data, right_hand_data

    def contains_features(self, mp_res):
        if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, self.solution.HAND_CONNECTIONS)


# region manual tests
def init_detector_manually(processor_type: str = "RAW"):
    m_detector = HandDetector()
    m_detector.stream = stream.Webcam()
    m_detector.initialize_model()

    if processor_type == "RAW":
        m_detector.observer = events.PrintRawDataUpdate()
    else:
        from ..cgt_bridge import print_bridge
        bridge = print_bridge.PrintBridge
        target = hand_processing.HandProcessor(bridge)
        m_detector.observer = events.DriverDebug(target)

    m_detector.listener = events.UpdateListener()
    m_detector.listener.attach(m_detector.observer)
    return m_detector


if __name__ == '__main__':
    detection_type = "image"

    detector = init_detector_manually("PROCESSED")

    if detection_type == "image":
        for _ in range(50):
            detector.image_detection()
    else:
        detector.stream_detection()

    del detector
# endregion
