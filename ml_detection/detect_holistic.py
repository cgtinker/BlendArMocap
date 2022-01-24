import mediapipe as mp
from bridge import pose_drivers
from bridge import events
from ml_detection import abstract_detector
from utils.open_cv import stream
import importlib

importlib.reload(abstract_detector)
importlib.reload(pose_drivers)


class HolisticDetector(abstract_detector.RealtimeDetector):
    def image_detection(self):
        with self.solution.Holistic(
                min_detection_confidence=0.7,
                static_image_mode=True,
        ) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.Holistic(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                static_image_mode=False,
        ) as mp_lib:
            while self.stream.capture.isOpened():
                state = self.exec_detection(mp_lib)
                if state == {'CANCELLED'}:
                    return {'CANCELLED'}

    def initialize_model(self):
        self.solution = mp.solutions.holistic

    def init_bpy_bridge(self):
        # TODO: requires multiple listeners. also requires a special observer pattern.
        target = pose_drivers.BridgePose()
        self.observer = events.BpyUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_debug_logs(self):
        self.observer = events.PrintRawDataUpdate()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
        face, pose, l_hand, r_hand = None, None, None, None
        if mp_res.pose_landmarks:
            pose = self.cvt2landmark_array(mp_res.pose_landmarks)
        if mp_res.face_landmarks:
            face = self.cvt2landmark_array(mp_res.face_landmarks)
        if mp_res.left_hand_landmarks:
            l_hand = self.cvt2landmark_array(mp_res.left_hand_landmarks)
        if mp_res.right_hand_landmarks:
            r_hand = self.cvt2landmark_array(mp_res.right_hand_landmarks)
        return [face, pose, l_hand, r_hand]

    def contains_features(self, mp_res):
        if not mp_res.pose_landmarks:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        mp_drawings.draw_landmarks(
            s.frame,
            mp_res.face_landmarks,
            self.solution.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.drawing_style
                .get_default_face_mesh_contours_style())
        mp_drawings.draw_landmarks(
            s.frame,
            mp_res.pose_landmarks,
            self.solution.POSE_CONNECTIONS,
            landmark_drawing_spec=self.drawing_style
                .get_default_pose_landmarks_style())
        mp_drawings.draw_landmarks(
            s.frame, mp_res.left_hand_landmarks, self.solution.HAND_CONNECTIONS)
        mp_drawings.draw_landmarks(
            s.frame, mp_res.right_hand_landmarks, self.solution.HAND_CONNECTIONS)


# region manual tests
def image_detection(tracking_handler):
    for i in range(50):
        tracking_handler.image_detection()

    del tracking_handler


def stream_detection(tracking_handler):
    tracking_handler.stream_detection()


def init_test():
    tracking_handler = HolisticDetector()

    tracking_handler.stream = stream.Webcam()
    tracking_handler.initialize_model()
    tracking_handler.init_debug_logs()
    tracking_handler.listener.attach(tracking_handler.observer)
    return tracking_handler


if __name__ == '__main__':
    handler = init_test()
    #image_detection(handler)
    stream_detection(handler)

    del handler
# endregion
