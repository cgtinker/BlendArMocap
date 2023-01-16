from . import cgt_mp_interface, cgt_mp_preferences, cgt_mp_detection_operator, cgt_mp_properties


classes = [
    cgt_mp_properties,
    cgt_mp_detection_operator,
    cgt_mp_interface,
    cgt_mp_preferences
]


def register():
    for cls in classes:
        if cls is None:
            continue
        cls.register()


def unregister():
    for cls in reversed(classes):
        if cls is None:
            continue
        cls.unregister()
