from abc import abstractmethod
import bpy


class DriverProperties:
    """ Driver expression include Driver Properties same as the Driver Interface.
        The properties are required to set up the Driver. """
    target_object = None
    provider_obj = None

    property_type: str
    property_name: str

    data_paths: list
    functions: list = None
    target_rig: bpy.types.Object = None


class Driver(DriverProperties):
    """ Applies a driver to a targeted object using values gathered from a
        provider object. May stores multiple drivers and variables """
    drivers: list
    assigned: bool = False
    variables: list

    def __init__(self, expression: DriverProperties):
        if self.assigned is True:
            return

        self.target_object = expression.target_object
        self.provider_obj = expression.provider_obj
        self.property_type = expression.property_type
        self.property_name = expression.property_name
        self.data_paths = expression.data_paths
        self.functions = expression.functions
        self.target_rig = expression.target_rig

        if self.functions is None:
            self.functions = ["", "", ""]

        self.drivers = [self.target_object.driver_add(self.property_type, index) for index in range(3)]
        self.variables = [d.driver.variables.new() for d in self.drivers]

        self.prepare()
        self.apply()

    @abstractmethod
    def prepare(self):
        pass

    def apply(self):
        for idx, d in enumerate(self.drivers):
            d.driver.expression = "(" + self.functions[idx] + "(" + self.variables[idx].name + "))" if self.functions[
                idx] else self.variables[idx].name
