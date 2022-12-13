'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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
