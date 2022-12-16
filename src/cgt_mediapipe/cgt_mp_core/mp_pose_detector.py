'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import mediapipe as mp

from . import cv_stream, mp_detector_node

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


class PoseDetector(mp_detector_node.DetectorNode):
    def __init__(self, *args, **kwargs):
        mp_detector_node.DetectorNode.__init__(self, *args, **kwargs)
        self.solution = mp.solutions.pose

    # https://google.github.io/mediapipe/solutions/pose#python-solution-api
    def update(self):
        # BlazePose GHUM 3D
        with self.solution.Pose(
                static_image_mode=True,
                model_complexity=1,
                # model_complexity=2,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.Pose(
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                static_image_mode=False,
                smooth_segmentation=True
        ) as mp_lib:
            while self.stream.capture.isOpened():
                state = self.exec_detection(mp_lib)
                if state == {'CANCELLED'}:
                    return {'CANCELLED'}

    def detected_data(self, mp_res):
        return self.cvt2landmark_array(mp_res.pose_world_landmarks)

    def empty_data(self):
        return [[]]

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
    detector = PoseDetector(cv_stream.Stream(0))

    for _ in range(50):
        data = detector.update()
        print(data)

    del detector
# endregion
