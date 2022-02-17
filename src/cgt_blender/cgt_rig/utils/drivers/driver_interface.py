from abc import ABC, abstractmethod

import bpy


class Expression(ABC):
    target_object = None

    variables: list

    property_type: str
    property_name: str

    data_paths: list
    functions: list = None

    @abstractmethod
    def set(self):
        pass


class Driver(ABC):
    """ Applies a driver to a targeted object using values gathered from a
        provider object. May stores multiple drivers and variables """
    target_object: bpy.types.Object
    provider_obj: bpy.types.Object

    drivers: list
    variables: list

    property_type: str
    property_name: str

    data_paths: list
    functions: list = None

    target_rig: bpy.types.Object = None
    assigned: bool = True

    def init(self):
        if self.assigned is True:
            return

        if self.functions is None:
            self.functions = ["", "", ""]

        self.drivers = [self.target_object.driver_add(self.property_type, index).driver for index in range(3)]
        self.variables = [driver.variables.new() for driver in self.drivers]

    @abstractmethod
    def prepare(self):
        pass

    def apply(self):
        for idx, driver in enumerate(self.drivers):
            driver.expression = "(" + self.functions[idx] + "(" + self.variables[idx].name + "))" \
                if self.functions[idx] else self.variables[idx].name
