from abc import ABC, abstractmethod

import bpy


class Expression(ABC):
    @abstractmethod
    def get_expressions(self):
        pass

class JointLenght(Expression):
    def get_expressions(self):
        pass

class Driver(ABC):
    driver_target: bpy.types.Object
    provider_obj: bpy.types.Object

    drivers: list
    variables: list

    property_type: str
    property_name: str

    data_paths: list
    functions: list = None

    target_rig = None
    assigned: bool = True

    @abstractmethod
    def prepare(self):
        pass

    def init(self):
        if self.assigned is True:
            return

        if self.functions is None:
            self.functions = ["", "", ""]

        self.drivers = [self.driver_target.driver_add(self.property_type, index).driver for index in range(3)]
        self.variables = [driver.variables.new() for driver in self.drivers]

    def apply(self):
        for idx, driver in enumerate(self.drivers):
            driver.expression = "(" + self.functions[idx] + "(" + self.variables[idx].name + "))" \
                if self.functions[idx] else self.variables[idx].name


class SinglePropertyDriver(Driver):
    def prepare(self):
        for idx, var in enumerate(self.variables):
            var.name = self.property_name
            var.type = 'SINGLE_PROP'

            try:
                var.targets[0].id = self.provider_obj
                var.targets[0].data_path = self.data_paths[idx]
            except ReferenceError:
                print(f"Failed to set driver {self.property_name} to {self.driver_target.name}")


class BonePropertyDriver(Driver):
    def prepare(self):
        for idx, variable in enumerate(self.variables):
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


class PoseDriver:
    """
    name: str = None
    driver_type: DriverType = DriverType.limb_driver
    length: float = .0
    offset: list = [.0, .0, .0]
    expressions: list = None
    target_rig: bpy.types.Object = None

    def __init__(self, name):
        self.name = name
"""

    @staticmethod
    def get_detected_joint_length_expression(driver_target):
        return [
            driver_target, "location", "length",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]
        ]

    @staticmethod
    def get_detected_joint_head_expression(driver_target):
        return [
            driver_target, "location", "prev_pos",
            ["location.x", "location.y", "location.z"],
            ["", "", ""]
        ]
