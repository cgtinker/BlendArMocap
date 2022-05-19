import mediapipe as mp

from . import detector_interface
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
        target = hand_processing.BridgeHand()
        self.observer = events.BpyUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_debug_logs(self):
        target = hand_processing.BridgeHand()
        # self.observer = events.DriverDebug(target)
        self.observer = events.PrintRawDataUpdate()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
        # multi_hand_world_landmarks // multi_hand_landmarks
        return (
            [self.cvt2landmark_array(hand) for hand in mp_res.multi_hand_world_landmarks],
            self.cvt_hand_orientation(mp_res.multi_handedness)
        )

    def contains_features(self, mp_res):
        if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, self.solution.HAND_CONNECTIONS)


# region manual tests
def image_detection(tracking_handler):
    for _ in range(50):
        tracking_handler.image_detection()


def stream_detection(tracking_handler):
    tracking_handler.stream_detection()


def init_test():
    tracking_handler = HandDetector()

    tracking_handler.stream = stream.Webcam()
    tracking_handler.initialize_model()
    tracking_handler.init_debug_logs()
    tracking_handler.listener.attach(tracking_handler.observer)
    return tracking_handler


if __name__ == '__main__':
    handler = init_test()
    image_detection(handler)
    # stream_detection(handler)

    del handler
# endregion
