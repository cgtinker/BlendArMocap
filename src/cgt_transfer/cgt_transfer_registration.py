from . import (
    cgt_tf_object_properties,
    cgt_tf_3dview_panel,
    cgt_tf_operators,
    cgt_tf_properties_panel,
    cgt_tf_io_config
)

modules = [
    cgt_tf_object_properties,
    cgt_tf_3dview_panel,
    cgt_tf_operators,
    cgt_tf_properties_panel,
    cgt_tf_io_config,
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
