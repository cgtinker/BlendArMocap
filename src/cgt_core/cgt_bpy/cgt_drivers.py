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
import bpy
import logging
from typing import Dict, Optional, List, Union
from . import cgt_object_prop
from dataclasses import dataclass


@dataclass(frozen=True)
class CgtPropertyType(object):
    loc = 'location'
    scale = 'scale'
    rot = 'rotation_euler'
    quart = 'rotation_quaternion'


@dataclass(frozen=True)
class CgtVariableType(object):
    transforms = 'TRANSFORMS'
    single_prop = 'SINGLE_PROP'


@dataclass(repr=True)
class CgtDriver(object):
    # Apply Properties to:
    target_obj: Union[bpy.types.Object, bpy.types.PoseBone]
    property_type: CgtPropertyType
    expressions: Dict[str]

    # Provide Properties using:
    variable_type: CgtVariableType
    provider_obj: Optional[Union[bpy.types.Object, bpy.types.PoseBone]]
    property_name: Optional[str]
    data_paths: Optional[Dict[int, str]]
    transforms_space: Optional[str]

    # Internal:
    _drivers: Dict[int, List[bpy.types.FCurve]] = None
    _variables: Dict[int, bpy.types.DriverVariable] = None

    def __init__(self,
                 target: Union[bpy.types.Object, bpy.types.PoseBone] = None,
                 property_type: CgtPropertyType = None,
                 expressions: Dict[int, str] = None,

                 provider_obj: Optional[Union[bpy.types.Object, bpy.types.PoseBone]] = None,
                 property_name: Optional[str] = None,
                 data_paths: Optional[Dict[int, str]] = None,
                 variable_type: Optional[CgtVariableType] = CgtVariableType.single_prop,
                 transforms_space: Optional[str] = "WORLD_SPACE"):
        """
        Create a driver using a unique property name as custom data to avoid overwrites.
           :param target Union[bpy.types.Object, bpy.types.PoseBone]: Driver gets applied to target object.
           :param property_type PropertyType: Property type that gets influenced by the driver. [loc, scale, rot, quart]
           :param expressions Dict[str]=None: Dict of driver expressions b.e. { 0: 'frame*unique_str', 1: 'frame*3', 2: 'frame' }.

           :param variable_type: CgtVariableType: Define variable type to use. [transforms, single_prop]
           :param provider_obj Optional[Union[bpy.types.Object, bpy.types.PoseBone]]: Access properties from provider obj.
           :param property_name: Optional[str]: Name of the provided property. (unique_str)
           :param data_path: Optional[Dict[str]]: Data paths of the provided property. { 0: location[0], 2: location[2] }
           :param transforms_space: Optional[str] = "WORLD_SPACE": Space when using variable type transform. ["WORLD_SPACE", "LOCAL_SPACE", POSE_SPACE"]

        """
        if expressions is None:
            expressions = {}

        self.target_obj = target
        self.provider_obj = provider_obj
        self.property_type = property_type
        self.property_name = property_name
        self.expressions = expressions
        self.data_paths = data_paths
        self.variable_type = variable_type
        self.transforms_space = transforms_space

        self._drivers = dict()
        self._variables = dict()
        self.post_init()

    def post_init(self):
        """ Adds FCurves to the target object which are required in the driver set up process. """
        assert self.target_obj is not None
        assert self.property_type is not None
        assert len(self.data_paths) == len(self.expressions)

        if self.provider_obj is None:
            # point to obj holding property paths
            self.provider_obj = self.target_obj

        for idx, value in self.expressions.items():
            # don't add driver if there won't be an expression
            driver = self.target_obj.driver_add(str(self.property_type), int(idx))
            self._drivers[int(idx)] = driver

    def apply(self):
        """ Sets driver variables and applies driver expressions. """
        self.set_driver_variables()
        self.apply_driver_expression()

    def set_driver_variables(self):
        """ Sets the driver variables for single prop and transform prop drivers.
            Currently, supports PoseBones and Objects. """
        if self.property_name is None:
            logging.debug(f"Property name not set, aborted driver preparation: {self}")
            return

        if not cgt_object_prop.set_custom_property(obj=self.target_obj, prop_name=self.property_name, value=-1):
            logging.debug(f"Property has been set previously, aborted driver preparation: {self}")
            return

        if self.variable_type == CgtVariableType.single_prop:
            self.init_single_prop_driver()
        elif self.variable_type == CgtVariableType.transforms:
            self.init_transforms_driver()
        else:
            logging.error("Unknown type inserted.")
            raise TypeError

    def init_single_prop_driver(self):
        """ Init a single property value, data path has to be provided. """
        for idx, driver in self._drivers.items():
            if self.data_paths is None:
                continue

            # create new variable
            variable = driver.driver.variables.new()
            variable.name = self.property_name
            variable.type = 'SINGLE_PROP'

            # set target and data path
            if isinstance(self.provider_obj, bpy.types.Object):
                variable.targets[0].id = self.provider_obj
                variable.targets[0].data_path = self.data_paths[idx]
            elif isinstance(self.provider_obj, bpy.types.PoseBone):
                variable.targets[0].id = self.provider_obj.id_data
                variable.targets[0].data_path = f'pose.bones.["{self.provider_obj.name}"].{self.data_paths[idx]}'
            else:
                raise TypeError

    def init_transforms_driver(self):
        """ Using transform values of pose bones to access their props in global space.
            Set up a new init method for single props if you need head/ tail coords. """
        for idx, driver in self._drivers.items():
            if self.data_paths is None:
                continue

            # create new variable
            variable = driver.driver.variables.new()
            variable.name = self.property_name
            variable.type = 'TRANSFORMS'

            # set variable target
            if isinstance(self.provider_obj, bpy.types.Object):
                variable.targets[0].id = self.provider_obj
            elif isinstance(self.provider_obj, bpy.types.PoseBone):
                variable.targets[0].id = self.provider_obj.id_data
                variable.targets[0].bone_target = self.provider_obj.name
            else:
                raise TypeError

            trans_path = {
                "location[0]":       'LOC_X',
                "location[1]":       'LOC_Y',
                "location[2]":       'LOC_Z',
                "rotation_euler[0]": 'ROT_X',
                "rotation_euler[1]": 'ROT_Y',
                "rotation_euler[2]": 'ROT_Z',
                "scale[0]":          'SCALE_X',
                "scale[1]":          'SCALE_Y',
                "scale[2]":          'SCALE_Z',
            }

            # apply data paths and transform type
            variable.targets[0].transform_space = self.transforms_space
            data_path = trans_path[self.data_paths.get(idx, None)]
            variable.targets[0].transform_type = data_path

    def apply_driver_expression(self):
        """ Add the expressions to the driver. """
        logging.debug(f"Attempt to set driver expression: {self}")
        for i, d in self._drivers.items():
            d.driver.expression = self.expressions[i] if self.expressions[i] else ""
