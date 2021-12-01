from ml_detection import hand
from utils import log
from utils.open_cv import stream
from bridge import events


def main():
    log.init_logger('debug')
    s = stream.Webcam()

    # observe data
    _observer = events.UpdatePrinter()
    _listener = events.UpdateListener()
    _listener.attach(_observer)

    hand.main(s, _listener)
    del s


if __name__ == '__main__':
    main()
