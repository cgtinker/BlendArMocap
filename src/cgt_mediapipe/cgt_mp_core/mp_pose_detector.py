import mediapipe as mp

from . import cv_stream, mp_detector_node


class PoseDetector(mp_detector_node.DetectorNode):
    def __init__(self, stream, pose_model_complexity: int = 1, min_detection_confidence: float = 0.7):
        mp_detector_node.DetectorNode.__init__(self, stream)
        self.pose_model_complexity = pose_model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.solution = mp.solutions.pose

    # https://google.github.io/mediapipe/solutions/pose#python-solution-api
    def update(self, data, frame):
        # BlazePose GHUM 3D
        with self.solution.Pose(
                static_image_mode=True,
                model_complexity=self.pose_model_complexity,
                min_detection_confidence=self.min_detection_confidence) as mp_lib:
            return self.exec_detection(mp_lib), frame

    def detected_data(self, mp_res):
        return self.cvt2landmark_array(mp_res.pose_world_landmarks)

    def empty_data(self):
        return []

    def contains_features(self, mp_res):
        if not mp_res.pose_world_landmarks:
            return False
        return True

    def draw_result(self, s, mp_res, mp_drawings):
        mp_drawings.draw_landmarks(
            s.frame,
            mp_res.pose_landmarks,
            self.solution.POSE_CONNECTIONS,
            landmark_drawing_spec=self.drawing_style.get_default_pose_landmarks_style())


# region manual tests
if __name__ == '__main__':
    from . import cv_stream
    from ...cgt_core.cgt_calculators_nodes import mp_calc_pose_rot
    detector = PoseDetector(cv_stream.Stream(0))
    calc = mp_calc_pose_rot.PoseRotationCalculator()
    frame = 0
    for _ in range(50):
        frame += 1
        data, frame = detector.update(None, frame)
        data, frame = calc.update(data, frame)
        print(data)

    del detector
# endregion
