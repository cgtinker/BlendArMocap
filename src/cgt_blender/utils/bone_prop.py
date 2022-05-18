from dataclasses import dataclass

from .driver_interface import DriverProperties, DriverType, ObjectType
from .mapping import CustomProps


@dataclass(repr=True)
class CustomBoneProp(DriverProperties):
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
        self.target_type = ObjectType.OBJECT
        if not prop_name == "":
            self.custom_target_props = CustomProps(
                prop_name, prop_values
            )
        self.provider_obj = provider_obj
        self.provider_type = ObjectType.BONE
        self.target_rig = True
        self.driver_type = DriverType.CUSTOM

        self.overwrite = True
        self.property_type = property_type
        self.property_name = prop_name
        self.data_paths = [f'pose.bones["{provider_obj}"]["{prop_name}"]']*3
        self.functions = ["", "", ""]
