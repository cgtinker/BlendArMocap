from . import cgt_mp_interface, cgt_mp_preferences, cgt_dependencies

detection_operator = None
if all(cgt_dependencies.dependencies_installed):
    from . import cgt_mp_detection_operator
    detection_operator = cgt_mp_detection_operator


classes = [
    detection_operator,
    cgt_mp_interface,
    cgt_mp_preferences
]


def register():
    for cls in classes:
        if cls is None:
            continue
        cls.register()


def unregister():
    for cls in classes:
        if cls is None:
            continue
        cls.unregister()
