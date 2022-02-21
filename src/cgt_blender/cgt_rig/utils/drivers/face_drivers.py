from .driver_interface import DriverProperties


# from ...abs_rigging import DriverType

def get_target_axis(axis):
    """target only a specifc scale axis"""
    target_axis = []
    for tar_axis in ["X", "Y", "Z"]:
        if tar_axis == axis:
            target_axis.append("scale." + tar_axis.lower())
        else:
            target_axis.append("")

    return target_axis


class EyeDriver(DriverProperties):
    def __init__(self, provider_obj, target_axis, avg_distance, factor):
        """ Provides eye driver properties.
            :param provider_obj: object providing scale values.
            :param target_axis: target axis to set datapath [X, Y, Z].
            :param avg_distance: base distance from rigify right.
            :param factor: scale attr factorized.
        """
        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.data_paths = get_target_axis(target_axis)
        self.functions = ["", "", f"{avg_distance}*{factor}"]


class MouthDriver(DriverProperties):
    mouth_attr_dict = {
        "up":    [".3", "Z"],
        "down":  ["-.3", "Z"],
        "left":  [".05", "X"],
        "right": ["-.05", "X"]
    }

    def __init__(self, provider_obj, avg_distance, target_axis):
        factor, axis = self.mouth_attr_dict[target_dir]
        functions = []
        for tar_axis in ["X", "Y", "Z"]:
            if tar_axis == axis:
                func = f"{avg_distance}*{factor}*"
            else:
                func = ""
            functions.append(func)

        self.provider_obj = provider_obj
        self.property_type = "location"
        self.property_name = "scale"
        self.data_paths = get_target_axis(target_axis)
        self.functions = ["", "", f"{avg_distance}*{factor}"]

        attribute = self.get_loc_sca_driver_attribute(target, self.get_target_axis(axis), functions)
