# TODO: Transfer will be part of core
from . import (
    object_properties
)
from .interface import (
    cgt_transfer_panel,
    cgt_transfer_operators,
    cgt_driver_prop_panel
)

modules = [
    object_properties,
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
