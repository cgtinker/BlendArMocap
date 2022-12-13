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

from abc import ABC, abstractmethod
from src.cgt_core.cgt_naming import COLLECTIONS


class CustomData:
    idx = None
    loc = None
    rot = None
    sca = None
    obj = None


class BridgeInterface(ABC):
    parent_col = COLLECTIONS.drivers
    prev_rotation = {}

    @abstractmethod
    def get_instances(self):
        pass

    @abstractmethod
    def set_position(self, data, frame):
        pass

    @abstractmethod
    def set_rotation(self, data, frame):
        pass

    @abstractmethod
    def set_scale(self, data, frame):
        pass
