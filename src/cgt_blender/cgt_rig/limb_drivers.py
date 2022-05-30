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

from ..utils.driver_interface import DriverProperties, DriverContainer, DriverType, ObjectType
from dataclasses import dataclass


# region Bone Center Driver
# region Properties
@dataclass(repr=True)
class LeftBone(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.provider_type = ObjectType.BONE
        self.property_type = "location"
        self.property_name = "left"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class RightBone(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.provider_type = ObjectType.BONE
        self.property_type = "location"
        self.property_name = "right"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = [f".5*((left)+(right))",
                          f".5*((left)+(right))",
                          f".5*((left)+(right))"]


# endregion
@dataclass(repr=True)
class BoneCenter(DriverContainer):
    def __init__(self, driver_target, bones, target_rig):
        left_bone = LeftBone(bones[0])
        right_bone = RightBone(bones[1])

        self.pose_drivers = [left_bone, right_bone]

        for driver in self.pose_drivers:
            driver.target_object = driver_target
            driver.target_rig = target_rig
            driver.driver_type = DriverType.BONE
# endregion


# region Limb Driver
# region Properties
@dataclass(repr=True)
class JointLength(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "length"
        self.data_paths = ["scale.z", "scale.z", "scale.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class PreviousPosition(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "prev_pos"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class DriverOrigin(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "origin"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class MainExpression(DriverProperties):
    target_object: str = ""
    functions: list = None

    def __init__(self, provider_obj, bone_length):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "loc"
        self.data_paths = ["location.x", "location.y", "location.z"]

        self.functions = [f"(origin)+{bone_length}/(length)*(-(prev_pos)+(loc))",
                          f"(origin)+{bone_length}/(length)*(-(prev_pos)+(loc))",
                          f"(origin)+{bone_length}/(length)*(-(prev_pos)+(loc))"]


# endregion

@dataclass(repr=True)
class LimbDriver(DriverContainer):
    def __init__(self, driver_target, driver_origin, detected_joint, rigify_joint_length):
        """ Generates drivers for limbs which. As limps for a chain, the drivers may depend on each other. """
        # previous driver as origin
        driver_origin = DriverOrigin(driver_origin)

        # detected results for mapping
        joint_head = PreviousPosition(detected_joint[0])
        joint_length = JointLength(detected_joint[1])
        joint_tail = MainExpression(detected_joint[1], rigify_joint_length)

        # setup drivers
        self.pose_drivers = [driver_origin, joint_head, joint_length, joint_tail]

        # set reoccurring props
        for driver in self.pose_drivers:
            driver.target_object = driver_target
            driver.target_rig = None
            driver.driver_type = DriverType.SINGLE

# endregion

