from abc import abstractmethod
from dataclasses import dataclass

import bpy

from ....utils import objects


@dataclass(frozen=True)
class DriverType:
    LIMB: int = 0
    CONSTRAINT: int = 1
    face_driver: int = 2
    SINGLE: int = 3
    BONE: int = 4
    CUSTOM: int = 5


class DriverProperties:
    """ Driver expression include Driver Properties same as the Driver Interface.
        The properties are required to set up the Driver.
        :params
        target_object - driver gets added to obj
        provider_obj - obj providing values for driver"""
    target_object = None
    provider_obj = None

    property_type: str
    property_name: str

    data_paths: list
    functions: list = None
    target_rig: bpy.types.Object = None
    overwrite: bool = False


@dataclass(repr=True)
class DriverContainer:
    """ Container for storing multiple drivers. """
    pose_drivers: list = None


@dataclass(repr=True)
class Driver(DriverProperties):
    """ Applies a driver to a targeted object using values gathered from a
        provider object. May stores multiple drivers and variables. """
    drivers: list
    variables: list
    assigned: bool = False

    def is_custom_property_assigned(self):
        # return if custom prop has been assigned
        self.assigned = objects.set_custom_property(self.target_object, self.property_name, True)

    def __init__(self, expression: DriverProperties):
        # requirements to check custom props
        self.target_object = expression.target_object
        self.property_name = expression.property_name
        self.overwrite = expression.overwrite

        # prevent to apply driver twice
        self.is_custom_property_assigned()
        if self.assigned is True and self.overwrite is False:
            return

        self.functions = expression.functions

        # overwrite driver expression
        if self.overwrite is True:

            try:
                self.drivers = [
                    self.target_object.animation_data.drivers.remove(
                        self.target_object.animation_data.drivers[index]
                    ) for index in range(3)]
            except IndexError:
                pass

        # setup vars for new driver
        self.property_type = expression.property_type
        self.provider_obj = expression.provider_obj
        self.data_paths = expression.data_paths
        self.target_rig = expression.target_rig

        if self.functions is None:
            self.functions = ["", "", ""]

        # generate drivers
        self.drivers = [self.target_object.driver_add(self.property_type, index) for index in range(3)]
        self.variables = [d.driver.variables.new() for d in self.drivers]

        # prepare and apply driver to obj
        self.prepare()
        self.apply()

    @abstractmethod
    def prepare(self):
        pass

    def apply(self):
        for idx, d in enumerate(self.drivers):
            d.driver.expression = self.functions[idx] if self.functions[idx] else "0"
