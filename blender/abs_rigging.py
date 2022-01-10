from abc import ABC


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
    
    @staticmethod
    def add_driver(source_obj, target_obj, prop, dataPath,
                   index=-1, negative=False, func=''):
        ''' Add driver to obj prop (at index), driven by target dataPath '''

        if index != -1:
            driver = source_obj.driver_add(prop, index).driver
        else:
            driver = source_obj.driver_add(prop).driver

        variable = driver.variables.new()
        variable.name = prop
        variable.targets[0].id = target_obj
        variable.targets[0].data_path = dataPath

        driver.expression = func + "(" + variable.name + ")" if func else variable.name
        driver.expression = driver.expression if not negative else "-1 * " + driver.expression



