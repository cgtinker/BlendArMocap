
from __future__ import  annotations
from typing import Tuple
import bpy
import rigify # noqa
from src.cgt_core.cgt_bpy import cgt_object_prop
from src.cgt_core.cgt_bpy.cgt_drivers import DriverFactory, Distance, RotationalDifference, SingleProperty, TransformChannel


def add_remap_properties(
        factory: DriverFactory, name: str,
        min_in: float, max_in: float, min_out: float, max_out: float) -> Tuple[str, str]:

    slope = (max_out - min_out) / (max_in - min_in)
    offset = min_out - slope * min_in

    slope_name = f"{name}_factor"
    offset_name = f"{name}_offset"
    cgt_object_prop.set_custom_property(factory.target, slope_name, slope)
    cgt_object_prop.set_custom_property(factory.target, offset_name, offset)
    return slope_name, offset_name


def add_simple_remap_expression(
        factory: DriverFactory, name: str, data_path: str, idx: int,
        slope_name: str, offset_name: str) -> DriverFactory:

    # factory, slope_name, offset_name = add_remap_properties()
    props = [
        SingleProperty(slope_name, factory.target, f'["{slope_name}"]'),
        SingleProperty(offset_name, factory.target, f'["{offset_name}"]'),
    ]
    for prop in props:
        factory.add_variable(prop, data_path, idx)

    expr = f"{slope_name} * {name} + {offset_name}"
    factory.add_expression(expr, data_path, idx)
    return factory
