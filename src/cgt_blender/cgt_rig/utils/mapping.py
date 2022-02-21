from dataclasses import dataclass


@dataclass(repr=True)
class MappingRelation:
    source: object
    values: object
    driver_type: int

    def __init__(self, source: object, driver_type: int, values: object):
        self.source = source
        self.driver_type = driver_type
        self.values = values