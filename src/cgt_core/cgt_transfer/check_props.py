from __future__ import annotations

from typing import List

from . import cgt_driver_obj_props


def check_value_mapping_generic_props(props: List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]) -> List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]:
    """ Copy values from first container and set axis explicit. """
    main_prop = props[0]
    if main_prop.remap_default == 'DEFAULT':
        main_prop.remap_default = 'XYZ'
    target_axis = [axis for axis in main_prop.remap_default]

    for tar_axis, prop in zip(target_axis, props):
        if not prop.active:
            continue
        prop.remap_details = tar_axis
        prop.factor = main_prop.factor
        prop.offset = main_prop.offset
        prop.from_min = main_prop.from_min
        prop.from_max = main_prop.from_max
        prop.to_min = main_prop.to_min
        prop.to_max = main_prop.to_max
    return props


def check_value_mapping_detail_props(props: List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]) -> List[cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping]:
    """ Sets explicit axis names and checks for overlaps. """
    axis_d = {0: 'X', 1: 'Y', 2: 'Z'}

    for i, prop in enumerate(props):
        if prop.remap_details in ['X', 'Y', 'Z']:
            continue

        prop.remap_details = axis_d[i]

    active_props = [prop for prop in props if prop.active]
    assert len(set(active_props)) == len(active_props)
    return props