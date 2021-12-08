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
    mp_pose = mp.solutions.pose

    log.logger.info('INITIALIZE POSE DETECTION')
    with mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=False,
    ) as mp_lib:
        while stream.capture.isOpened():
            stream.update()
            if not stream.updated:
                # break if loading video file
                log.logger.debug("Ignoring empty camera frame")
                continue

            mp_res = helper.detect_features(mp_lib, stream)

            # draw stream and stop processing if no landmarks are available
            if not mp_res.pose_landmarks:
                stream.draw()
                if stream.exit_stream():
                    break
                continue

            # process ml data as send to bridge
            listener.data = helper.cvt2landmark_array(mp_res.pose_landmarks)
            listener.notify()

            # render
            draw_pose(stream, mp_res, mp_drawings, mp_drawing_styles, mp_pose)
            stream.draw()
            if stream.exit_stream():
                break


def draw_pose(stream, mp_res, mp_drawing, mp_drawing_styles, mp_pose):
    """Draws the landmarks and the connections on the image."""
    mp_drawing.draw_landmarks(
        stream.frame,
        mp_res.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())


if __name__ == "__main__":
    log.init_logger()
    helper.init_main(s, events, main)
