from .driver_interface import DriverProperties


class JointLength(DriverProperties):
    def __init__(self, target_object, **kwargs):
        self.target_object = target_object
        self.property_type = "location"
        self.property_name = "length"
        self.data_paths = ["scale.z", "scale.z", "scale.z"]
        self.functions = ["", "", ""]


class JointHead(DriverProperties):
    def __init__(self, target_object, **kwargs):
        self.target_object = target_object
        self.property_type = "location"
        self.property_name = "prev_pos"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class DriverOrigin(DriverProperties):
    def __init__(self, target_object, **kwargs):
        self.target_object = target_object
        self.property_type = "location"
        self.property_name = "origin"
        self.data_paths = ["location.x", "location.y", "location.z"]
        self.functions = ["", "", ""]


class MainExpression(DriverProperties):
    offset: list = [.0, .0, .0]

    def __init__(self, target_object, **kwargs):
        self.target_object = target_object
        self.property_type = "location"
        self.property_name = "loc"
        self.data_paths = ["location.x", "location.y", "location.z"]

        if kwargs['offset'] is not None:
            self.offset = kwargs['offset']

        self.functions = [f"({self.offset[0]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+",
                          f"({self.offset[1]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+",
                          f"({self.offset[2]}+origin))+{kwargs['length']}/(length)*(-(prev_pos)+"]


class LimbDriver:
    joint_length: JointLength
    joint_head: JointHead
    driver_origin: DriverOrigin
    main_expression: MainExpression

    drivers: list = None

    def __init__(self):
        self.drivers = [self.joint_length, self.joint_head, self.driver_origin, self.main_expression]
        pass
