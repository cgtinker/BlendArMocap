from __future__ import annotations

from interfaces import observer_pattern as op
from typing import List
from utils import log


class UpdateListener(op.Listener):
    """ Listens to updates of mp-ml tracking data and notifies receivers. """
    _observers: List[op.Observer] = []
    data = None

    def attach(self, observer: op.Observer) -> None:
        log.logger.debug("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: op.Observer) -> None:
        log.logger.debug("Subject: Detached an observer")
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)


class UpdatePrinter(op.Observer):
    """ Prints updated data for debugging """
    def update(self, subject: op.Listener) -> None:
        print(subject.data)


class BpyHandUpdateReceiver(op.Observer):
    def update(self, subject: op.Listener) -> None:
        print(subject.data)


class BpyPoseUpdateReceiver(op.Observer):
    def update(self, subject: op.Listener) -> None:
        print(subject.data)


class BpyFaceUpdateReceiver(op.Observer):
    def update(self, subject: op.Listener) -> None:
        print(subject.data)
