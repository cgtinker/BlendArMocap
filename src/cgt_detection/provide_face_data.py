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

from . import realtime_data_provider_interface, stream

from typing import Mapping, Tuple
from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions.drawing_utils import DrawingSpec


class FaceDetector(realtime_data_provider_interface.RealtimeDataProvider):
    # https://google.github.io/mediapipe/solutions/face_mesh#python-solution-api
    def frame_detection_data(self):
        with self.solution.FaceMesh(
                max_num_faces=1,
                static_image_mode=False,
                refine_landmarks=True,
                min_detection_confidence=0.7) as mp_lib:
            return self.exec_detection(mp_lib)

    def stream_detection(self):
        with self.solution.FaceMesh(
                max_num_faces=1,
                min_detection_confidence=0.8,
                min_tracking_confidence=0.5,
                refine_landmarks=True,
                static_image_mode=False,
        ) as mp_lib:
            while self.stream.capture.isOpened():
                state = self.exec_detection(mp_lib)
                if state == {'CANCELLED'}:
                    return {'CANCELLED'}

    def initialize_model(self):
        self.solution = mp.solutions.face_mesh

    def get_detection_results(self, mp_res):
        return [self.cvt2landmark_array(landmark) for landmark in mp_res.multi_face_landmarks]

    def contains_features(self, mp_res):
        if not mp_res.multi_face_landmarks:
            return False
        return True

    @staticmethod
    def get_custom_face_mesh_contours_style() -> Mapping[Tuple[int, int], DrawingSpec]:
        _THICKNESS_CONTOURS = 2

        _RED = (48, 48, 255)
        _WHITE = (224, 224, 224)

        _FACEMESH_CONTOURS_CONNECTION_STYLE = {
            face_mesh_connections.FACEMESH_LIPS:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_LEFT_EYE:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_LEFT_EYEBROW:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_RIGHT_EYE:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_RIGHT_EYEBROW:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
            face_mesh_connections.FACEMESH_FACE_OVAL:
                DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
        }

        face_mesh_contours_connection_style = {}
        for k, v in _FACEMESH_CONTOURS_CONNECTION_STYLE.items():
            for connection in k:
                face_mesh_contours_connection_style[connection] = v
        return face_mesh_contours_connection_style

    def draw_result(self, s, mp_res, mp_drawings):
        """Draws the landmarks and the connections on the image."""
        for face_landmarks in mp_res.multi_face_landmarks:
            self.drawing_utils.draw_landmarks(
                image=self.stream.frame,
                landmark_list=face_landmarks,
                connections=self.solution.FACEMESH_CONTOURS,
                connection_drawing_spec=self.get_custom_face_mesh_contours_style(),
                # connection_drawing_spec=self.drawing_style.get_default_face_mesh_contours_style(),
                landmark_drawing_spec=None)

                # image=self.stream.frame,
                # landmark_list=face_landmarks,
                # connections=self.solution.FACEMESH_IRISES,
                # landmark_drawing_spec=None,
                # connection_drawing_spec=self.drawing_style.get_default_face_mesh_iris_connections_style())


# region manual tests
def init_detector_manually(processor_type: str = "RAW"):
    m_detector = FaceDetector()
    m_detector.stream = stream.Webcam()
    m_detector.initialize_model()

    from ..cgt_patterns import events
    if processor_type == "RAW":
        m_detector.observer = events.PrintRawDataUpdate()
    else:
        from ..cgt_bridge import print_bridge
        from ..cgt_processing import face_processing
        bridge = print_bridge.PrintBridge
        target = face_processing.FaceProcessor(bridge)
        m_detector.observer = events.DriverDebug(target)

    m_detector.listener = events.UpdateListener()
    m_detector.listener.attach(m_detector.observer)
    return m_detector


if __name__ == '__main__':
    detection_type = 'image'
    detector = init_detector_manually("PROCESSED")

    if detection_type == "image":
        for _ in range(50):
            detector.frame_detection_data()
    else:
        detector.stream_detection()

    del detector
# endregion
