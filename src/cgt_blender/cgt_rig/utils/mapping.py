from dataclasses import dataclass


@dataclass(repr=True)
class Slope:
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


@dataclass(repr=True)
class CustomProps:
    name: str
    value: float
    v_min: float
    v_max: float
    use_soft: bool

    def __init__(self, name, value, v_min=None, v_max=None, use_soft=False):
        self.name = name
        self.value = value
        self.v_min = v_min
        self.v_max = v_max
        self.use_soft = use_soft
