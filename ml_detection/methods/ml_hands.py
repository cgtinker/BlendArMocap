import mediapipe as mp
from bridge import events
from custom_data import cd_hand
from ml_detection.methods import helper
from interfaces.abc_bridge_model import BridgeModel


class HandDetectionBridge(BridgeModel):
    def initialize_model(self):
        solution_type = mp.solutions.hands
        solution_target = solution_type.Hands
        return solution_type, solution_target

    def get_drawing_solutions(self):
        drawing_utils = mp.solutions.drawing_utils
        drawing_style = mp.solutions.drawing_styles
        return drawing_utils, drawing_style

    def initialize_bridge(self):
        target = cd_hand.Hand()
        observer = events.BpyHandUpdateReceiver(target)
        listener = events.UpdateListener()
        return observer, listener

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
        """Draws the landmarks and the connections on the image."""
        for hand in mp_res.multi_hand_landmarks:
            mp_drawings.draw_landmarks(s.frame, hand, mp_hands.HAND_CONNECTIONS)
