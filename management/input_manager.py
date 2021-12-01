from ml_detection import face, hand, pose
from bridge import events
from utils import log
from utils.open_cv import stream


def face_tracking():
    log.logger.info("attempt to track face")
    start_detection(face, events.BpyFaceUpdateReceiver)


def hand_tracking():
    log.logger.info("attempt to track hand")
    start_detection(hand, events.BpyHandUpdateReceiver)


def pose_tracking():
    log.logger.info("attempt to track hand")
    start_detection(pose, events.BpyPoseUpdateReceiver)


def start_detection(model, observer):
    s = stream.Webcam()
    _observer = observer()
    _listener = events.UpdateListener()
    _listener.attach(_observer)
    model.main(s, _listener)
    pass
