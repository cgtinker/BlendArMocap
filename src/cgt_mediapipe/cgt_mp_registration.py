from . import cgt_mp_interface

classes = [
    cgt_mp_interface
]


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in classes:
        cls.unregister()
