# TODO: Transfer will be part of core
from . import (
    cgt_driver_obj_props,
    cgt_driver_prop_panel
)
from .interface import (
    cgt_transfer_panel,
    cgt_transfer_operators
)

modules = [
    cgt_driver_obj_props,
    cgt_driver_prop_panel,
    cgt_transfer_operators,
    cgt_transfer_panel,
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
