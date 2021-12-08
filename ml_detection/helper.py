from mediapipe.framework.formats import landmark_pb2, classification_pb2
from utils import log


def init_helper(s, events, main):
    """ helper method to init main detection functions for debugging purposes """

    log.logger.debug('ACCESS WEBCAM STREAM')
    _stream = s.Webcam()

    log.logger.debug('ATTEMPT TO OBSERVE DATA')
    _observer = events.UpdatePrinter()
    _listener = events.UpdateListener()
    _listener.attach(_observer)

    log.logger.debug('START RUNNING')
    main(_stream, _listener)
    del _stream


def detect_features(mp_lib, stream):
    """ handles flags, conversion and detects features in frame """
    stream.frame.flags.writeable = False
    stream.set_color_space('rgb')
    mp_res = mp_lib.process(stream.frame)
    stream.set_color_space('bgr')
    return mp_res


def cvt2landmark_array(landmark_list: landmark_pb2):
    """landmark_list: A normalized landmark list proto message to be annotated on the image."""
    return [[idx, [landmark.x, landmark.y, landmark.z]] for idx, landmark in enumerate(landmark_list.landmark)]


def cvt_hand_orientation(orientation: classification_pb2):
    """ data sample:
    classification {
        index: 1
        score: 0.9790361523628235
        label: "Right"
    }"""
    if not orientation:
        return None

    return [[idx, "Right" in str(o)] for idx, o in enumerate(orientation)]
