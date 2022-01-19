import importlib
from abc import ABC

from utils import m_V

importlib.reload(m_V)


def copy_rotation(constraint, target, *args):
    constraint.target = target
    constraint.euler_order = 'XYZ'
    constraint.influence = 1
    constraint.mix_mode = 'ADD'
    constraint.owner_space = 'LOCAL'


def copy_location(constraint, target, *args):
    print("copy location", constraint, target, args)
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'POSE'


def add_driver(obj, target, prop, dataPath,
               index=-1, negative=False, func=''):
    ''' Add driver to obj prop (at index), driven by target dataPath '''

    if index != -1:
        driver = obj.driver_add(prop, index).limb_driver
    else:
        driver = obj.driver_add(prop).limb_driver

    variable = driver.variables.new()
    variable.name = prop
    variable.targets[0].id = target
    variable.targets[0].data_path = dataPath

    driver.expression = func + "(" + variable.name + ")" if func else variable.name
    driver.expression = driver.expression if not negative else "-1 * " + driver.expression


class BpyRigging(ABC):
    driver_mapping = {
        "shoulder_distance": ("scale", "position")
    }

    constraint_mapping = {
        "CAMERA_SOLVER": 0,
        "FOLLOW_TRACK": 1,
        "OBJECT_SOLVER": 2,
        "COPY_LOCATION": copy_location,
        "COPY_ROTATION": copy_rotation,
        "COPY_SCALE": 5,
        "COPY_TRANSFORMS": 6,
        "LIMIT_DISTANCE": 7,
        "LIMIT_LOCATION": 8,
        "LIMIT_ROTATION": 9,
        "LIMIT_SCALE": 10,
        "MAINTAIN_VOLUME": 11,
        "TRANSFORM": 12,
        "TRANSFORM_CACHE": 13,
        "CLAMP_TO": 14,
        "DAMPED_TRACK": 15,
        "IK": 16,
        "LOCKED_TRACK": 17,
        "SPLINE_IK": 18,
        "STRETCH_TO": 19,
        "TRACK_TO": 20,
        "ACTION": 21,
        "ARMATURE": 22,
        "CHILD_OF": 23,
        "FLOOR": 24,
        "FOLLOW_PATH": 25,
        "PIVOT": 26,
        "SHRINKWRAP": 27,
    }

    def add_constraint(self, bone, target, constraint):
        constraints = [c for c in bone.constraints]

        # removing previously added constraints if types match
        for c in constraints:
            # setup correct syntax for comparison
            constraint_name = c.name
            constraint_name = constraint_name.replace(" ", "_")
            constraint_name = constraint_name.upper()
            # remove match
            if constraint_name == constraint:
                bone.constraints.remove(c)

        # adding a new constraint
        m_constraint = bone.constraints.new(
            type=constraint
        )
        # set the constraint type and execute its custom method
        self.constraint_mapping[constraint](m_constraint, target)

    def add_driver_batch(self, driver_target, driver_source,
                         prop_source, prop_target, data_path, func=None):
        """ Add driver to object on x-y-z axis. """
        # check if custom prop has been added to the driver
        added = self.set_custom_property(driver_target, prop_target, True)

        if added is True:
            if func is None:
                func = ['', '', '']

            # add driver
            for i in range(3):
                self.add_driver(driver_target, driver_source, prop_source, prop_target, data_path[i], i, func[i])
        else:
            print("driver cannot be applied to same ob twice", driver_target.name)

    @staticmethod
    def add_driver(target_obj, driver_obj, prop, prop_target,
                   dataPath, index=-1, func=''):
        ''' Add driver to obj prop (at index), driven by target dataPath '''

        if index != -1:
            driver = target_obj.driver_add(prop, index).driver
        else:
            driver = target_obj.driver_add(prop).driver

        variable = driver.variables.new()
        variable.name = prop_target
        variable.targets[0].id = driver_obj
        variable.targets[0].data_path = dataPath

        driver.expression = func + "(" + variable.name + ")" if func else variable.name

    def set_custom_property(self, target_obj, prop_name, prop):
        if self.get_custom_property(target_obj, prop_name) == None:
            target_obj[prop_name] = prop
            return True
        else:
            return False

    @staticmethod
    def get_custom_property(target_obj, prop_name):
        try:
            value = target_obj[prop_name]
        except KeyError:
            value = None

        return value

    def get_average_scale(self, joint_bones, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
            returns the average length of the connected bones. """
        arm_joints = self.get_joints(joint_bones, pose_bones)
        distances = []
        for joint in arm_joints:
            dist = m_V.get_vector_distance(joint[0], joint[1])
            distances.append(dist)
        avg_dist = sum(distances) / len(distances)
        return avg_dist

    @staticmethod
    def get_joints(joint_names, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
        returns the bone head locations in the same formatting. """
        arm_joints = []
        for names in joint_names:

            joint = []
            for name in names:
                bone_pos = pose_bones[name].head
                joint.append(bone_pos)

            arm_joints.append(joint)
        return arm_joints