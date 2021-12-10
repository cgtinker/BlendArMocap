import mediapipe as mp
from bridge import events
from ml_detection.abstract_detector import RealtimeDetector
from utils.open_cv import stream


class PoseDetector(RealtimeDetector):
    def image_detection(self):
        with self.solution.Pose(
                static_image_mode=True,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.Pose(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                static_image_mode=False,
        ) as mp_lib:
            while self.stream.capture.isOpened():
                state = self.exec_detection(mp_lib)
                if state == {'CANCELLED'}:
                    return {'CANCELLED'}

    def initialize_model(self):
        self.solution = mp.solutions.pose
        self.drawing_utils = mp.solutions.drawing_utils
        self.drawing_style = mp.solutions.drawing_styles

    def init_bpy_bridge(self):
        pass

    def init_debug_logs(self):
        self.observer = events.UpdatePrinter()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
        return self.cvt2landmark_array(mp_res.pose_landmarks)

    def contains_features(self, mp_res):
        if not mp_res.pose_landmarks:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        mp_drawings.draw_landmarks(
            s.frame,
            mp_res.pose_landmarks,
            self.solution.POSE_CONNECTIONS,
            landmark_drawing_spec=self.drawing_style.get_default_pose_landmarks_style())


# region manual tests
def image_detection(tracking_handler):
    for i in range(50):
        tracking_handler.image_detection()

    del tracking_handler


def stream_detection(tracking_handler):
    tracking_handler.stream_detection()


def init_test():
    tracking_handler = PoseDetector()

    tracking_handler.stream = stream.Webcam()
    tracking_handler.initialize_model()
    tracking_handler.init_debug_logs()
    tracking_handler.listener.attach(tracking_handler.observer)
    return tracking_handler


if __name__ == '__main__':
    handler = init_test()
    # image_detection(handler)
    stream_detection(handler)

    del handler
# endregion
