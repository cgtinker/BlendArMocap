from . import fm_interface
from . import fm_operators

modules = [
    fm_operators,
    fm_interface
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()

