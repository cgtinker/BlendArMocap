from .driver_interface import DriverProperties, DriverContainer, DriverType
from dataclasses import dataclass


# region Bone Center Driver
# region Properties
@dataclass(repr=True)
class LeftBone(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "left"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class RightBone(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "right"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = [".5)*(left+", ".5)*(left+", ".5)*(left+"]


# endregion
@dataclass(repr=True)
class BoneCenter(DriverContainer):
    def __init__(self, driver_target, bones, target_rig):
        left_bone = LeftBone(bones[0])
        right_bone = RightBone(bones[1])

        self.pose_drivers = [left_bone, right_bone]
        self.set(driver_target, DriverType.BONE, target_rig)


# endregion


# region Limb Driver
# region Properties
@dataclass(repr=True)
class JointLength(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "length"
        self.data_paths = ["scale.z", "scale.z", "scale.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class PreviousPosition(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "prev_pos"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class DriverOrigin(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "origin"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


@dataclass(repr=True)
class MainExpression(DriverProperties):
    target_object: str
    functions: list

    def __init__(self, provider_obj, bone_length):
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "loc"
        self.data_paths = ["location.x", "location.y", "location.z"]

        self.functions = [f"(origin))+{bone_length}/(length)*(-(prev_pos)+",
                          f"(origin))+{bone_length}/(length)*(-(prev_pos)+",
                          f"(origin))+{bone_length}/(length)*(-(prev_pos)+"]


# endregion

@dataclass(repr=True)
class LimbDriver(DriverContainer):
    def __init__(self, driver_target, driver_origin, detected_joint, rigify_joint_length):
        # previous driver as origin
        driver_origin = DriverOrigin(driver_origin)

        # detected results for mapping
        joint_head = PreviousPosition(detected_joint[0])
        joint_length = JointLength(detected_joint[1])
        joint_tail = MainExpression(detected_joint[1], bone_length=rigify_joint_length)

        self.pose_drivers = [driver_origin, joint_head, joint_length, joint_tail]
        self.set(driver_target, DriverType.SINGLE)

# endregion
