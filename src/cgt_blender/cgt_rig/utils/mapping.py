from dataclasses import dataclass
from math import radians


@dataclass(repr=True)
class MappingRelation:
    driver_source: object
    driver_target: object
    driver_type: int
    values: list

    def __init__(self, driver_source: object, driver_type: int, driver_target: object, values: list = None):
        self.driver_source = driver_source
        self.driver_type = driver_type
        self.driver_target = driver_target
        if values is None:
            values = []
        self.values = values


@dataclass(repr=True)
class Slope:
    slope: float
    min_in: float
    min_out: float

    def __init__(self, min_in, max_in, min_out, max_out):
        self.slope = (max_out - min_out) / (max_in - min_in)
        self.min_in = min_in
        self.min_out = min_out