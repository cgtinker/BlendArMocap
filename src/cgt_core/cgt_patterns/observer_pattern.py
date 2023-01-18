from __future__ import annotations
from abc import ABC, abstractmethod


# The Subject class maintains a list of observers and has methods
# for attaching and detaching observers. It also has a method
# for notifying all observers of state changes.
class Subject(ABC):
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


# The Observer class has a method, update, that is called by the
# subject when the subject's state changes.
class Observer(ABC):
    """The Observer interface declares the update method, used by subjects."""
    @abstractmethod
    def update(self, subject: Subject) -> None:
        """Receive update from subject."""
        pass
