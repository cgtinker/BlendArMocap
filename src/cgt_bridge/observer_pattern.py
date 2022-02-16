from __future__ import annotations
from abc import ABC, abstractmethod


class Listener(ABC):
    """The Subject interface declares a set of methods for managing subscribers."""

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self) -> None:
        """Notify all observers about an event."""
        pass


class Observer(ABC):
    """The Observer interface declares the update method, used by subjects."""

    @abstractmethod
    def update(self, subject: Listener) -> None:
        """Receive update from subject."""
        pass
