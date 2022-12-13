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

from . import cgt_driver_interface


class SinglePropDriver(cgt_driver_interface.Driver):
    """ Prepares a single property driver targeting an object. """
    def prepare(self):
        for idx, var in enumerate(self.variables):
            var.name = self.property_name
            var.type = 'SINGLE_PROP'

            try:
                var.targets[0].id = self.provider_obj
                var.targets[0].data_path = self.data_paths[idx]
            except ReferenceError:
                print(f"Failed to set driver {self.property_name} to {self.target_object.name}")


class BonePropDriver(cgt_driver_interface.Driver):
    """ Prepares a single property driver targeting a bone. """
    def prepare(self):
        for idx, variable in enumerate(self.variables):
            variable.name = self.property_name
            variable.type = 'TRANSFORMS'
            variable.targets[0].id = self.target_rig
            variable.targets[0].bone_target = self.provider_obj.name
            trans_path = {
                "location.x": 'LOC_X',
                "location.y": 'LOC_Y',
                "location.z": 'LOC_Z',
                "rotation.x": 'ROT_X',
                "rotation.y": 'ROT_Y',
                "rotation.z": 'ROT_Z',
                "scale.x":    'SCALE_X',
                "scale.y":    'SCALE_Y',
                "scale.z":    'SCALE_Z',
            }
            variable.targets[0].transform_space = 'WORLD_SPACE'
            variable.targets[0].transform_type = trans_path[self.data_paths[idx]]


class CustomBonePropDriver(cgt_driver_interface.Driver):
    """ Creates a custom property driver targeting a custom property of a bone. """
    def prepare(self):
        for idx, var in enumerate(self.variables):
            var.name = self.property_name
            var.type = 'SINGLE_PROP'
            var.targets[0].id = self.target_rig
            var.targets[0].bone_target = f'pose.bones["{self.provider_obj.name}"]["{self.property_name}"]'
            var.targets[0].data_path = self.data_paths[idx]

