from __future__ import annotations

from typing import List

from ..cgt_patterns import observer_pattern as op
from ..cgt_processing import processor_interface


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

    def update(self, _listener: UpdateListener) -> None:
        print(_listener.data)


class DriverDebug(op.Observer):
    """ Doesn't apply data but useful for debugging purposes. """

    def __init__(self, _processor: processor_interface.DataProcessor = None):
        if _processor is None:
            raise BrokenPipeError

        self.processor = _processor
        self.processor.init_references()

    def update(self, _listener: UpdateListener) -> None:
        self.processor.data = _listener.data
        self.processor.frame = _listener.frame
        self.processor.init_print()
        self.processor.update()


class HolisticDriverDebug(op.Observer):
    def __init__(self, processors: list):
        if None in processors:
            raise BrokenPipeError

        self.processors = processors
        for processor in self.processors:
            processor.init_references()

    def update(self, _listener: UpdateListener) -> None:
        for idx, processor in enumerate(self.processors):
            processor.data = _listener.data[idx]
            processor.frame = _listener.frame
            processor.init_print()
            processor.update()


class BpyUpdateReceiver(op.Observer):
    """ Updates empties in realtime via modal operator. """
    def __init__(self, _processor: processor_interface.DataProcessor = None):
        if _processor is None:
            raise BrokenPipeError

        self.processor = _processor
        self.processor.init_references()

    def update(self, _listener: UpdateListener) -> None:
        self.processor.data = _listener.data
        self.processor.frame = _listener.frame
        self.processor.init_data()
        self.processor.update()


class HolisticBpyUpdateReceiver(op.Observer):
    def __init__(self, processors: list):
        if None in processors:
            raise BrokenPipeError

        self.processors = processors
        for processor in self.processors:
            processor.init_references()

    def update(self, _listener: UpdateListener) -> None:
        for idx, processor in enumerate(self.processors):
            if len(_listener.data[idx][0]) < 1:
                print("data not updated")
                continue

            processor.data = _listener.data[idx]
            processor.frame = _listener.frame
            processor.init_data()
            processor.update()

    def __del__(self):
        del self.processors

