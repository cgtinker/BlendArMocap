import mediapipe as mp

from . import abstract_detector
from ..cgt_bridge import events, face_processing
from ..cgt_utils import stream

from typing import Mapping, Tuple
from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions.drawing_utils import DrawingSpec


class FaceDetector(abstract_detector.RealtimeDetector):
    def image_detection(self):
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

    def init_bpy_bridge(self):
        target = face_processing.BridgeFace()
        self.observer = events.BpyUpdateReceiver(target)
        self.listener = events.UpdateListener()

    def init_driver_logs(self):
        target = face_processing.BridgeFace()
        self.observer = events.DriverDebug(target)
        self.listener = events.UpdateListener()

    def init_raw_data_printer(self):
        self.observer = events.PrintRawDataUpdate()
        self.listener = events.UpdateListener()

    def process_detection_result(self, mp_res):
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
def image_detection(tracking_handler):
    for i in range(50):
        tracking_handler.image_detection()
    print('FINISHED')
    del tracking_handler


def stream_detection(tracking_handler):
    tracking_handler.stream_detection()


def init_test():
    tracking_handler = FaceDetector()

    tracking_handler.stream = stream.Webcam()
    tracking_handler.initialize_model()
    # tracking_handler.init_driver_logs()
    tracking_handler.init_raw_data_printer()
    tracking_handler.listener.attach(tracking_handler.observer)
    return tracking_handler


if __name__ == '__main__':
    handler = init_test()
    image_detection(handler)
    # stream_detection(handler)

    del handler
# endregion
