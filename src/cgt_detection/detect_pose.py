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

from pathlib import Path
import bpy 
import mediapipe as mp

from . import detector_interface

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


class PoseDetector(detector_interface.RealtimeDetector):
    # https://google.github.io/mediapipe/solutions/pose#python-solution-api
    def image_detection(self):
        if self.input_type == 2: #this is freemocap data
            freemocap_session_path = Path(bpy.context.scene.m_cgtinker_mediapipe.freemocap_session_path)
            self.load_freemocap_mediapipe3d_data(freemocap_session_path)
            return

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

    def initialize_model(self):
        self.solution = mp.solutions.pose

    def get_detection_results(self, mp_res):
        return self.cvt2landmark_array(mp_res.pose_world_landmarks)

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
def init_detector_manually(processor_type: str = "RAW"):
    m_detector = PoseDetector()
    from ..cgt_utils import stream
    m_detector.stream = stream.Webcam()
    m_detector.initialize_model()

    from ..cgt_patterns import events
    if processor_type == "RAW":
        m_detector.observer = events.PrintRawDataUpdate()
    else:
        from ..cgt_bridge import print_bridge
        from ..cgt_processing import pose_processing
        bridge = print_bridge.PrintBridge
        target = pose_processing.PoseProcessor(bridge)
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
