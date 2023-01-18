from dataclasses import dataclass


@dataclass(repr=True)
class Slope:
    """ Slope / Gradient gets used to change mapping ranges. """
    slope: float
    max_in: float
    max_out: float
    min_in: float
    min_out: float
    name: str

    def __init__(self, min_in, max_in, min_out, max_out, name=""):
        self.slope = (max_out - min_out) / (max_in - min_in)
        self.min_in = min_in
        self.min_out = min_out
        self.max_in = max_in
        self.max_out = max_out
        self.name = name


def remap(value, min_in, max_in, min_out, max_out):
    slope = (max_out - min_out) / (max_in - min_in)
    offset = min_out - slope * min_in
    return slope * value + offset
