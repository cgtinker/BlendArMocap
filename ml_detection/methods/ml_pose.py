import mediapipe as mp
from bridge import events
from custom_data import cd_hand
from ml_detection.methods import helper
from interfaces.abstract_detector import RealtimeDetector
from utils.open_cv import stream


class PoseDetector(RealtimeDetector):
    def image_detection(self):
        with self.solution_target(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_img_detection(mp_lib)

    def initialize_model(self):
        pass
    
    def set_drawing_solution(self):
        pass

    def init_bpy_bridge(self):
        pass

    def init_debug_logs(self):
        self.observer = events.UpdatePrinter()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
        pass

    def contains_features(self, mp_res):
        pass

    def draw_result(self, s, mp_res, mp_drawings, mp_hands):
        pass

if __name__ == '__main__':
   print("called")
