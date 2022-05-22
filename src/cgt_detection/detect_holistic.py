import mediapipe as mp

from . import detector_interface
from ..cgt_processing import pose_processing
from ..cgt_bridge import bpy_bridge_interface
from ..cgt_patterns import events
from ..cgt_utils import stream


class HolisticDetector(detector_interface.RealtimeDetector):
    # https://google.github.io/mediapipe/solutions/holistic#python-solution-api
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
        target = pose_processing.PoseProcessor(bridge=None)
        self.observer = events.BpyUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_debug_logs(self):
        self.observer = events.PrintRawDataUpdate()
        self.listener = events.UpdateListener()

    def get_detection_results(self, mp_res):
        # TODO - eval init
        face, pose, l_hand, r_hand = [], [], [], []
        if mp_res.pose_landmarks:
            pose = self.cvt2landmark_array(mp_res.pose_landmarks)
        if mp_res.face_landmarks:
            face = self.cvt2landmark_array(mp_res.face_landmarks)
        if mp_res.left_hand_landmarks:
            l_hand = [self.cvt2landmark_array(mp_res.left_hand_landmarks)]
        if mp_res.right_hand_landmarks:
            r_hand = [self.cvt2landmark_array(mp_res.right_hand_landmarks)]
        return [[l_hand, r_hand], [face], pose]

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
def init_detector_manually(processor_type: str = "RAW"):
    m_detector = HolisticDetector()
    m_detector.stream = stream.Webcam()
    m_detector.initialize_model()

    if processor_type == "RAW":
        m_detector.observer = events.PrintRawDataUpdate()
    else:
        from ..cgt_bridge import print_bridge
        from ..cgt_processing import hand_processing, face_processing, pose_processing
        bridge = print_bridge.PrintBridge
        hand_processor = hand_processing.HandProcessor(bridge)
        face_processor = face_processing.FaceProcessor(bridge)
        pose_processor = pose_processing.PoseProcessor(bridge)
        m_detector.observer = events.HolisticDriverDebug([hand_processor, face_processor, pose_processor])

    m_detector.listener = events.UpdateListener()
    m_detector.listener.attach(m_detector.observer)
    return m_detector


if __name__ == '__main__':
    detection_type = "image"

    detector = init_detector_manually("PROCESSED")

    if detection_type == "image":
        for _ in range(15):
            detector.image_detection()
    else:
        detector.stream_detection()

    del detector
# endregion
