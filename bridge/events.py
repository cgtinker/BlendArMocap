from __future__ import annotations

from bridge import observer_pattern as op
from typing import List
from utils import log


class UpdateListener(op.Listener):
    """ Listens to updates of mp-ml tracking data and notifies receivers. """
    _observers: List[op.Observer] = []
    data = None
    frame = 0

    def attach(self, observer: op.Observer) -> None:
        log.logger.debug("OBSERVER ATTACHED FROM UPDATE LISTENER")
        self._observers.append(observer)

    def detach(self, observer: op.Observer) -> None:
        log.logger.debug("OBSERVER DETACHED FROM UPDATE LISTENER")
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
    def __init__(self, _model):
        self.model = _model

    def update(self, subject: op.Listener) -> None:
        self.model.data = subject.data
        self.model.frame = subject.frame
        self.model.init_data()


class BpyUpdateReceiver(op.Observer):
    """ Updates empties in realtime via modal operator. """
    def __init__(self, _model):
        self.model = _model
        self.model.init_references()

    def update(self, subject: op.Listener) -> None:
        self.model.data = subject.data
        self.model.frame = subject.frame
        self.model.init_data()
        self.model.update()


class MemoryUpdateReceiver(op.Observer):
    """ Preserve changes in memory for async update. """
    def __init__(self, _hand):
        self.hand = _hand
        self.idx = 0

    def update(self, subject: op.Listener) -> None:
        self.idx += 1
        self.hand.allocate_memory(self.idx, subject.data)
