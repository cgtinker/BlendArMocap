from __future__ import annotations
import logging
from abc import abstractmethod
from typing import List
from .cgt_patterns.observer_pattern import Subject, Observer


class RealtimeDataProvider(Subject):
    _observers: List[Observer] = []
    data = None
    frame = 0

    def attach(self, observer: Observer) -> None:
        logging.debug(f"Observer attached to RealtimeDataProvider: {self.__class__.__name__}")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        logging.debug(f"Observer detached from RealtimeDataProvider: {self.__class__.__name__}")
        self._observers.remove(observer)

    @abstractmethod
    def notify(self) -> None:
        pass
