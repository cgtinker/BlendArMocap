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


def add_driver(obj, target, prop, dataPath,
               index=-1, negative=False, func=''):
    ''' Add driver to obj prop (at index), driven by target dataPath '''

    if index != -1:
        driver = obj.driver_add(prop, index).driver
    else:
        driver = obj.driver_add(prop).driver

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
        "COPY_LOCATION": 3,
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

        # removing previously added constraints
        for c in constraints:
            bone.constraints.remove(c)

        # adding a new constraint
        m_constraint = bone.constraints.new(
            type=constraint
        )
        # set the constraint type and execute its custom method
        self.constraint_mapping[constraint](m_constraint, target)

    def add_driver_batch(self, driver_target, driver_source,
                         prop_source, prop_target, data_path, func=None):
        if func is None:
            func = ['', '', '']

        for i in range(3):
            self.add_driver(driver_target, driver_source, prop_source, prop_target, data_path[i], i, func[i])

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


class BpyDriver:
    props = {
        'loc': 'location',
        'rot': 'rotation',
        'sca': 'scale'
    }

    axis = {
        'x': '.x',
        'y': '.y',
        'z': '.z'
    }

    driver_target = None
    driver_source = None
    prop_source = ""
    prop_target = ""
    data_path = None
    func = None

    def __init__(self, driver_target: object, driver_source: object,
                 prop_source: str, prop_target: str, data_path: list, func: list):
        self.driver_target = driver_target
        self.driver_source = driver_source
        self.prop_source = self.props[prop_source]
        self.prop_target = self.props[prop_target]
        self.data_path = [self.prop_target + self.axis[prop_axis] for prop_axis in data_path]
        self.func = func

    def add_driver_batch(self):
        if self.func is None:
            func = ['', '', '']

        for i in range(3):
            self.add_driver(
                self.data_path[i], i, self.func[i])

    def add_driver(self, data_path, index=-1, func=''):
        ''' Add driver to obj prop (at index), driven by target dataPath '''

        if index != -1:
            driver = self.driver_target.driver_add(self.prop_source, index).driver
        else:
            driver = self.driver_target.driver_add(self.prop_source).driver

        variable = driver.variables.new()
        variable.name = self.prop_target
        variable.targets[0].id = self.driver_source
        variable.targets[0].data_path = data_path

        driver.expression = func + "(" + variable.name + ")" if func else variable.name


def main():
    driver = BpyDriver("target", "source", "sca", "sca", ["x", "y", "z"], ["", "", ""])
    driver.target = "target"
    driver.source = "source"
    driver.prop_source = "sca"
    driver.prop_target = "sca"


if __name__ == '__main__':
    main()
