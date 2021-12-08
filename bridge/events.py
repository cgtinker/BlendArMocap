from __future__ import annotations

from interfaces import observer_pattern as op
from typing import List
from utils import log
from custom_data import cd_hand
import bpy


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


class UpdatePrinter(op.Observer):
    """ Prints updated data for debugging """
    def update(self, subject: op.Listener) -> None:
        print(subject.data)


# region Hand
class BpyHandUpdateReceiver(op.Observer):
    def __init__(self, _hand):
        self.hand = _hand
        self.idx = 0

    def update(self, subject: op.Listener) -> None:
        self.idx += 1
        self.hand.data = subject.data
        self.hand.set_position(self.idx)


class MemoryHandUpdateReceiver(op.Observer):
    def __init__(self, _hand):
        self.hand = _hand
        self.idx = 0

    def update(self, subject: op.Listener) -> None:
        self.idx += 1
        self.hand.allocate_memory(self.idx, subject.data)

# endregion


class BpyPoseUpdateReceiver(op.Observer):
    def update(self, subject: op.Listener) -> None:
        print(subject.data)


class BpyFaceUpdateReceiver(op.Observer):
    def update(self, subject: op.Listener) -> None:
        print(subject.data)
