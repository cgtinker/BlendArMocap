import mediapipe as mp
from bridge import events
from utils import log
from utils.open_cv import stream as s
from ml_detection import helper


def main(stream: s.Webcam,
         listener: events.op.Listener,
         min_detection_confidence: float = 0.8,
         min_tracking_confidence: float = 0.5,
         ):

    # data and display specs
    mp_drawings = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh

    log.logger.info('INITIALIZE FACE DETECTION')
    with mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=False,
            max_num_faces=1,
    ) as mp_lib:
        while stream.capture.isOpened():
            stream.update()
            if not stream.updated:
                # break if loading video file
                log.logger.debug("Ignoring empty camera frame")
                continue

            mp_res = helper.detect_features(mp_lib, stream)

            # draw stream and stop processing if no landmarks are available
            if not mp_res.multi_face_landmarks:
                stream.draw()
                if stream.exit_stream():
                    break
                continue

            # send converted data to bridge
            listener.data = [helper.cvt2landmark_array(landmark) for landmark in mp_res.multi_face_landmarks]
            listener.notify()

            # render
            draw_face(stream, mp_res, mp_drawings, mp_drawing_styles, mp_face_mesh)
            stream.draw()
            if stream.exit_stream():
                break


def draw_face(stream, mp_res, mp_drawing, mp_drawing_styles, mp_face_mesh):
    """Draws the landmarks and the connections on the image."""
    for face_landmarks in mp_res.multi_face_landmarks:
        mp_drawing.draw_landmarks(
            image=stream.frame,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_tesselation_style())


if __name__ == "__main__":
    log.init_logger()
    helper.init_main(s, events, main)