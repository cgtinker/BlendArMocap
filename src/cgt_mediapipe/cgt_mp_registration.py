from . import interface, preferences, dependencies

classes = [
    interface,
    preferences
]

if all(dependencies.dependencies_installed):
    from . import detection_operator
    classes.append(detection_operator)


def register():
    for cls in classes:
        cls.register()


def unregister():
    for cls in classes:
        cls.unregister()
