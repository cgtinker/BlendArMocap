from . import cgt_core_panel

classes = [
    cgt_core_panel
]


def register():
    from ..cgt_utils import cgt_logging
    cgt_logging.init()
    for cls in classes:
        cls.register()


def unregister():
    for cls in classes:
        cls.unregister()
