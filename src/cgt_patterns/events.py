from __future__ import annotations

from typing import List

from ..cgt_patterns import observer_pattern as op
from ..cgt_processing import processor_interface
from ..cgt_detection import detector_interface


class UpdateListener(op.Listener):
    """ Listens to updates of mp-ml tracking data and notifies receivers. """
    _observers: List[op.Observer] = []
    data = None
    frame = 0

    def attach(self, observer: op.Observer) -> None:
        print("OBSERVER ATTACHED FROM UPDATE LISTENER")
        self._observers.append(observer)

    def detach(self, observer: op.Observer) -> None:
        print("OBSERVER DETACHED FROM UPDATE LISTENER")
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)


class PrintRawDataUpdate(op.Observer):
    """ Prints updated data for debugging. """

    def update(self, subject: op.Listener) -> None:
        print(subject.data)


class DriverDebug(op.Observer):
    """ Doesnt apply data but usefull for debugging purposes. """

    def __init__(self, _model: processor_interface.DataProcessor = None):
        if _model is None:
            raise BrokenPipeError

        self.model = _model
        self.model.init_references()

    def update(self, subject: op.Listener) -> None:
        self.model.data = subject.data
        self.model.frame = subject.frame
        self.model.init_print()
        self.model.update()


class BpyUpdateReceiver(op.Observer):
    """ Updates empties in realtime via modal operator. """

    def __init__(self, _model: processor_interface.DataProcessor = None):
        if _model is None:
            raise BrokenPipeError

        self.model = _model
        self.model.init_references()

    def update(self, subject: detector_interface.RealtimeDetector) -> None:
        self.model.data = subject.data
        self.model.frame = subject.frame
        self.model.init_data()
        self.model.update()

