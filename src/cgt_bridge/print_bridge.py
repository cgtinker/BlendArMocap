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

from . import bridge_interface
from . import custom_data_container


class PrintBridge(bridge_interface.BridgeInterface):
    def __init__(self, target_type: str = "FACE"):
        print("PRINT BRIDGE GOT CALLED", target_type)
        self.target_type: str = target_type

    def get_instances(self):
        # this may doesn't match the requirements for every processor
        if self.target_type == "FACE":
            return [[], [custom_data_container.CustomData() for _ in range(0, 8)]]
        elif self.target_type == "HAND":
            return [], []
        elif self.target_type == "POSE":
            return [], custom_data_container.CustomData(), custom_data_container.CustomData()

    def set_position(self, data, frame):
        print(f"POSITION DATA at {frame}\n{data}")

    def set_rotation(self, data, frame):
        print(f"ROTATION DATA at {frame}\n{data}")

    def set_scale(self, data, frame):
        print(f"SCALE DATA at {frame}\n{data}")
