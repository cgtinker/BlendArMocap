from __future__ import annotations
import bpy
import logging
from typing import Any
from abc import abstractmethod
from collections import namedtuple

transform_modes = {'WORLD_SPACE', 'TRANSFORM_SPACE', 'LOCAL_SPACE'}
rotation_modes = {'AUTO', 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZYX', 'QUATERNION', 'SWING_TWIST_X', 'SWING_TWIST_Y',
                  'SWING_TWIST_Z'}


class Variable:
    name: str = None
    type: str = None
    obj: Any = None

    @abstractmethod
    def assign(self):
        pass

    def _set_variable(self, driver_variable: bpy.types.DriverVariable = None):
        self._validate(driver_variable)
        self.variable = driver_variable.driver.variables.new()
        self.variable.name = self.name
        self.variable.type = self.type

    def _set_variable_target(self, variable_target, obj):
        if isinstance(self.obj, bpy.types.PoseBone):
            variable_target.id = obj.id_data
            variable_target.bone_target = obj.name
        else:
            variable_target.id = obj

    def _validate(self, driver_variable):
        assert driver_variable is not None
        assert self.name is not None
        assert self.type in {'SINGLE_PROP', 'TRANSFORMS', 'ROTATION_DIFF', 'LOC_DIFF'}


class SingleProperty(Variable):
    path: str = None

    def __init__(self, name: str, obj: Any, path: str):
        self.type = 'SINGLE_PROP'
        self.name = name
        self.obj = obj
        self.path = path

    def assign(self, driver_variable: bpy.types.DriverVariable = None):
        self._set_variable(driver_variable)
        if isinstance(self.obj, bpy.types.PoseBone):
            self.variable.targets[0].id = self.obj.id_data
            self.variable.targets[0].data_path = f'pose.bones.["{self.obj.name}"].{self.path}'
        else:
            self.variable.targets[0].id = self.obj
            self.variable.targets[0].data_path = self.path


class TransformChannel(Variable):
    transform_type = None
    transform_space = None

    def __init__(self, name: str, obj: bpy.types.Object, transform: str, idx: int,
                 transform_space: str = 'WORLD_SPACE'):
        self.type = 'TRANSFORMS'
        self.name = name
        self.obj = obj
        self.transform_type = self.get_transform_type(transform, idx)
        self.transform_space = transform_space

    def _validated_transform_space(self, transform, transform_space):
        if transform == 'rotation_euler':
            assert transform_space in {'AUTO', 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZYX', 'QUATERNION', 'SWING_TWIST_X',
                                       'SWING_TWIST_Y', 'SWING_TWIST_Z'}
        else:
            assert transform_space in {'WORLD_SPACE', 'TRANSFORM_SPACE', 'LOCAL_SPACE'}

    def get_transform_type(self, transform, idx):
        assert transform in {'location', 'rotation_euler', 'scale'}
        assert 0 <= idx <= 3
        transform_type = {
            'location':       {0: 'LOC_X', 1: 'LOC_Y', 2: 'LOC_Z'},
            'rotation_euler': {0: 'ROT_X', 1: 'ROT_Y', 2: 'ROT_Z', 3: 'ROT_W'},
            'scale':          {0: 'SCALE_X', 1: 'SCALE_Y', 2: 'SCALE_Z', 3: 'SCALE_AVG'}
        }
        return transform_type[transform][idx]

    def assign(self, driver_variable: bpy.types.DriverVariable = None):
        self._set_variable(driver_variable)
        self._set_variable_target(self.variable.targets[0], self.obj)
        if isinstance(self.obj, bpy.types.PoseBone):
            self.variable.targets[0].id = self.obj.id_data
            self.variable.targets[0].bone_target = self.obj.name
        else:
            self.variable.targets[0].id = self.obj

        # apply data paths and transform type
        self.variable.targets[0].transform_space = self.transform_space
        self.variable.targets[0].transform_type = self.transform_type


class RotationalDifference(Variable):
    other_object: bpy.types.Object = None

    def __init__(self, name: str, obj: bpy.types.Object, other_obj: bpy.types.Object):
        self.type = 'ROTATION_DIFF'
        self.name = name
        self.obj = obj
        self.other_obj = other_obj

    def assign(self, driver_variable: bpy.types.DriverVariable = None):
        self._set_variable(driver_variable)
        self._set_variable_target(self.variable.targets[0], self.obj)
        self._set_variable_target(self.variable.targets[1], self.other_obj)


class Distance(Variable):
    other_obj: bpy.types.Object
    transform_space: str
    other_transform_space: str

    def __init__(self, name: str, obj: bpy.types.Object, other_obj: bpy.types.Object,
                 transform_space: str = 'WORLD_SPACE', other_transform_space: str = 'WORLD_SPACE'):
        self.type = 'LOC_DIFF'
        self.name = name
        self.obj = obj
        self.other_obj = other_obj
        assert transform_space and other_transform_space in {'WORLD_SPACE', 'TRANSFORM_SPACE', 'LOCAL_SPACE'}
        self.transform_space = transform_space
        self.other_transform_space = other_transform_space

    def assign(self, driver_variable: bpy.types.DriverVariable = None):
        self._set_variable(driver_variable)
        self._set_variable_target(self.variable.targets[0], self.obj)
        self.variable.targets[0].transform_space = self.transform_space
        self._set_variable_target(self.variable.targets[1], self.other_obj)
        self.variable.targets[1].transform_space = self.other_transform_space


DriverVariable = namedtuple('DriverVariable', ['variable', 'path', 'idx'])
DriverExpression = namedtuple('DriverExpression', ['expression', 'path', 'idx'])


class DriverFactory:
    expressions: dict

    def __init__(self, target: Any, type: str = 'SCRIPTED'):
        """ Init a driver factory
            params target: Property or Object in Blender with accessible data path.
            params type: Driver type to use. ['MAX', 'MIN', 'AVERAGE', 'SCRIPTED', 'SUM'], default = SCRIPTED.
        """
        assert type in ['MAX', 'MIN', 'AVERAGE', 'SCRIPTED', 'SUM']
        self.type = type
        self.target = target
        self.expressions = {}
        self._driver_variables = {}
        self.variables = list()

    def add_variable(self, variable: Variable, path: str, idx: int):
        """ Adds driver variable. """
        if idx is None:
            idx = -1
        self.variables.append(DriverVariable(variable, path, idx))

    def add_expression(self, expression: str, path: str, idx: int = None):
        """ Adds a driver expression. """
        if idx is None:
            idx = -1

        if path not in self.expressions:
            self.expressions[path] = {}
        if idx not in self.expressions[path]:
            self.expressions[path][idx] = None

        self.expressions[path][idx] = expression

    def expand_expression(self, expression: str, path: str, idx: int = None):
        """ Previous expression gets encapsulated and wrapped in a new expression.
            Make sure to use brackets to place the previous expression {}."""
        assert idx is not None
        assert "{}" in expression

        if path not in self.expressions:
            self.expressions[path] = {}
        if idx not in self.expressions[path]:
            self.expressions[path][idx] = ""

        previous = f"({self.expressions[path][idx]})"
        self.expressions[path][idx] = expression.format(previous)

    def _add_driver_variable(self, path: str, idx: int, driver_variable: Any):
        """ Adds a driver variable to the driver variables dict. """
        if path not in self._driver_variables:
            self._driver_variables[path] = {}
        if idx not in self._driver_variables[path]:
            self._driver_variables[path][idx] = None

        self._driver_variables[path][idx] = driver_variable

    def _in_driver_variables(self, path: str, idx: int):
        """ Checks if path and idx are in the driver variables dict. """
        if path not in self._driver_variables.keys():
            return False
        if idx not in self._driver_variables[path].keys():
            return False
        return True

    def driver_add_variable(self, path, idx):
        if idx == -1:
            return self.target.driver_add(path)
        return self.target.driver_add(path, idx)

    def execute(self):
        """ Adds driver variables to object and stores them. """
        for var in self.variables:
            driver_variable = self.driver_add_variable(var.path, var.idx)
            var.variable.assign(driver_variable)
            self._add_driver_variable(var.path, var.idx, driver_variable)

        """ Assign expression to driver variables, if necessary create new driver variables. """
        for str_key, dictionary in self.expressions.items():
            for int_key, expression in dictionary.items():
                if expression is None:
                    continue

                if not self._in_driver_variables(str_key, int_key):
                    self._add_driver_variable(str_key, int_key, self.driver_add_variable(str_key, int_key))

                if self.type == 'SCRIPTED':
                    self._driver_variables[str_key][int_key].driver.expression = expression
                else:
                    self._driver_variables[str_key][int_key].driver.type = self.type


if __name__ == '__main__':
    # some objs
    cube = bpy.data.objects['Cube']
    plane = bpy.data.objects['Plane']
    sphere = bpy.data.objects['Sphere']

    factory = DriverFactory(cube)

    prop = TransformChannel("test", plane, "location", 1, "LOCAL_SPACE")
    factory.add_variable(prop, 'location', 1)
    prop = SingleProperty("prop_name", sphere, 'rotation_euler[0]')
    factory.add_variable(prop, 'location', 2)
    prop = Distance("dist", sphere, plane)
    factory.add_variable(prop, 'location', 2)
    prop = RotationalDifference("rot", sphere, plane)
    factory.add_variable(prop, 'rotation_euler', 2)
    prop = SingleProperty("prop_nameok", cube, '["prop"]')
    factory.add_variable(prop, 'scale', 2)

    factory.add_expression("2*dist", 'location', 2)
    factory.add_expression("abs(-4+1+1)", 'rotation_euler', 0)

    factory.execute()
