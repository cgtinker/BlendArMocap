from dataclasses import dataclass


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
