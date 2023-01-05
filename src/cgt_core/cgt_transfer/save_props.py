from __future__ import annotations

from . import cgt_driver_obj_props


def is_set_mapping_property(prop: cgt_driver_obj_props.OBJECT_PGT_CGT_ValueMapping):
    # TODO: use only for "save prop validation"
    attrs = ['from_min', 'from_max', 'to_min', 'to_max', 'factor', 'offset']
    defaults = [0.0, 1.0, 0.0, 1.0, 1.0, 0.0]

    for attr, default in zip(attrs, defaults):
        if getattr(prop, attr, default) != default:
            return True
    return False
