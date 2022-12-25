# TODO: Transfer will be part of core
from . import (
    cgt_driver_obj_props,
    cgt_driver_prop_panel
)

modules = [
    cgt_driver_obj_props,
    cgt_driver_prop_panel
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
