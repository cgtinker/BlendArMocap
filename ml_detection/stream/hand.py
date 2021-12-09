import mediapipe as mp
import time
from bridge import events
from utils import log
from utils.open_cv import stream as s
from ml_detection.methods import helper
from custom_data import cd_hand


def main(stream: s.Webcam,
         listener: events.op.Listener,
         min_detection_confidence: float = 0.8,
         min_tracking_confidence: float = 0.5,
         max_recording_length: int = 10
         ):

    """Hand detection using active webcam stream.
    Attempting to stash tracking results for further processing."""
    # data and display specs
    mp_hands = mp.solutions.hands
    mp_drawings = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    start_time = time.time()
    idx = 0
    log.logger.info('INITIALIZE HAND DETECTION')
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
            # TODO: send frame to listener
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

            elif time.time() - start_time > max_recording_length:
                break


def draw_hands(stream, mp_res, mp_drawings, mp_hands):
    """Draws the landmarks and the connections on the image."""
    for hand in mp_res.multi_hand_landmarks:
        mp_drawings.draw_landmarks(stream.frame, hand, mp_hands.HAND_CONNECTIONS)


if __name__ == "__main__":
    log.init_logger()
    log.logger.debug('ACCESS WEBCAM STREAM')
    _stream = s.Webcam()

    log.logger.debug('ATTEMPT TO OBSERVE DATA')
    m_hand = cd_hand.Hand('memory')
    #_observer = events.UpdatePrinter()
    _observer = events.MemoryHandUpdateReceiver(m_hand)
    _listener = events.UpdateListener()
    _listener.attach(_observer)

    log.logger.debug('START RUNNING')
    main(_stream, _listener)
    del _stream

    #m_hand.write_json()
