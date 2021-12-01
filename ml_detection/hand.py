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
    mp_hands = mp.solutions.hands
    mp_drawings = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=False,
            max_num_hands=2,
    ) as mp_lib:
        while stream.capture.isOpened():
            stream.update()
            if not stream.updated:
                # break if loading video file
                log.logger.debug("Ignoring empty camera frame")
                continue

            mp_res = helper.detect_features(mp_lib, stream)

            # draw stream and stop processing if no landmarks are available
            if not mp_res.multi_hand_landmarks and not mp_res.multi_handedness:
                stream.draw()
                if stream.exit_stream():
                    break
                continue

            # send converted data to bridge
            listener.data = (
                [helper.cvt2landmark_array(hand) for hand in mp_res.multi_hand_landmarks],
                helper.cvt_hand_orientation(mp_res.multi_handedness)
            )
            listener.notify()

            # render
            draw_hands(stream, mp_res, mp_drawings, mp_hands)
            stream.draw()
            if stream.exit_stream():
                break


def draw_hands(stream, mp_res, mp_drawings, mp_hands):
    """Draws the landmarks and the connections on the image."""
    for hand in mp_res.multi_hand_landmarks:
        mp_drawings.draw_landmarks(stream.frame, hand, mp_hands.HAND_CONNECTIONS)


if __name__ == "__main__":
    helper.init_main(s, events, main)
