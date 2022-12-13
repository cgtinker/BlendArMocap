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

from src.cgt_core.cgt_bpy.cgt_drivers import cgt_driver_interface
from src.cgt_core.cgt_bpy.cgt_properties import cgt_object_prop


class CustomBoneProp(cgt_driver_interface.DriverProperties):
    target_object: str
    provider_obj = str
    functions: list

    def __init__(self,
                 driver_target: str,
                 provider_obj: str,
                 property_type: str,
                 prop_name: str,
                 prop_values):
        """ Custom property on a bone for remapping as driver prop.
            :param driver_target: driver using the custom prop
            :param provider_obj: bone containing the custom prop
            :param property_type: property type required by the driver
            :param prop_name: name of the custom prop
            :param prop_values: values of the custom prop
        """

        self.target_object = driver_target
        self.target_type = cgt_driver_interface.ObjectType.OBJECT
        if not prop_name == "":
            self.custom_target_props = cgt_object_prop.CustomProps(
                prop_name, prop_values
            )
        self.provider_obj = provider_obj
        self.provider_type = cgt_driver_interface.ObjectType.BONE
        self.target_rig = True
        self.driver_type = cgt_driver_interface.DriverType.CUSTOM

        self.property_type = property_type
        self.property_name = prop_name
        self.data_paths = [f'pose.bones["{provider_obj}"]["{prop_name}"]']*3
        self.functions = ["", "", ""]
