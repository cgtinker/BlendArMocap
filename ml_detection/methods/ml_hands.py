import mediapipe as mp
from bridge import events
from custom_data import cd_hand
from ml_detection.methods import helper
from interfaces.abstract_detector import RealtimeDetector
from utils.open_cv import stream


class HandDetector(RealtimeDetector):
    def image_detection(self):
        with self.solution_target(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_img_detection(mp_lib)

    def initialize_model(self):
        self.solution_type = mp.solutions.hands
        self.solution_target = self.solution_type.Hands

    def set_drawing_solution(self):
        self.drawing_utils = mp.solutions.drawing_utils
        self.drawing_style = mp.solutions.drawing_styles

    def init_bpy_bridge(self):
        target = cd_hand.Hand()
        self.observer = events.BpyHandUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_debug_logs(self):
        self.observer = events.UpdatePrinter()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
        return (
            [helper.cvt2landmark_array(hand) for hand in mp_res.multi_hand_landmarks],
            helper.cvt_hand_orientation(mp_res.multi_handedness)
        )

    def contains_features(self, mp_res):
        if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings, mp_hands):
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, mp_hands.HAND_CONNECTIONS)


if __name__ == '__main__':
    tracking_handler = HandDetector()

    tracking_handler.stream = stream.Webcam()
    tracking_handler.initialize_model()
    tracking_handler.set_drawing_solution()
    tracking_handler.init_debug_logs()
    tracking_handler.listener.attach(tracking_handler.observer)

    for i in range(50):
        tracking_handler.image_detection()

    del tracking_handler
