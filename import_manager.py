import importlib
import os
import sys

# has to be at root
PACKAGE = os.path.basename(os.path.dirname(__file__))

load_order = {
    'init':       [
        'blender.interface.ui_registration',
        'blender.interface.ui_panels',
        'blender.interface.ui_preferences',
        'blender.interface.ui_properties',
        'blender.interface.install_dependencies',
        'blender.interface.stream_detection_operator',
        'blender.interface',

        'blender.utils.objects',
        'blender.utils',

        'blender.rig.utils.drivers.assignment',
        'blender.rig.utils.drivers.driver_expression',
        'blender.rig.utils.drivers.limb_drivers',
        'blender.rig.utils.drivers.pose_driver_expressions',
        'blender.rig.utils.drivers',

        'blender.rig.utils.constraints',
        'blender.rig.utils',

        'blender.rig.abs_rigging',
        'blender.rig.rig_pose',
        'blender.rig.rigify_face',
        'blender.rig.rigify_hands',
        'blender.rig.rigify_pose'
    ],
    'management': [

    ],
    'detection':  [

    ],

}

initial_load_order = [
    'utils.errors',
    'utils.misc',
    '...',
]

utils_module_name = __name__ + '.utils'


def get_loaded_modules():
    prefix = __name__ + '.'
    return [name for name in sys.modules if name.startswith(prefix)]


def reload_modules():
    fixed_modules = set(reload_list)

    for name in get_loaded_modules():
        if name not in fixed_modules:
            del sys.modules[name]

    for name in reload_list:
        importlib.reload(sys.modules[name])


def compare_module_list(a, b):
    # Allow 'utils' to move around
    a_copy = list(a)
    a_copy.remove(utils_module_name)
    b_copy = list(b)
    b_copy.remove(utils_module_name)
    return a_copy == b_copy


def load_initial_modules():
    # gets initial load order
    load_list = [__name__ + '.' + name for name in initial_load_order]

    for i, name in enumerate(load_list):
        # import modules
        importlib.import_module(name)
        # compare with loaded modules
        module_list = get_loaded_modules()
        # min loaded vs max loaded
        expected_list = load_list[0: max(11, i + 1)]

        if not compare_module_list(module_list, expected_list):
            print(f'{PACKAGE}: initial load order mismatch after {name} '
                  f'- expected: \n, {expected_list} '
                  f'\nGot:\n, {module_list}')

    return load_list


def load_rigs():
    if not legacy_loaded:
        rig_lists.get_internal_rigs()
        metarig_menu.init_metarig_menu()


if PACKAGE in locals():
    reload_modules()
else:
    legacy_loaded = False

    load_list = load_initial_modules()

    from . import (rig_lists, metarig_menu)

    reload_list = reload_list_init = get_loaded_modules()

    if not compare_module_list(reload_list, load_list):
        print('!!! RIGIFY: initial load order mismatch - expected: \n', load_list, '\nGot:\n', reload_list)

load_rigs()

# PASS OUT TRY EXCEPT
try:
    if PACKAGE in locals():
        print(f'{PACKAGE}: RELOADING!')
        """reloading"""
    else:
        print(f'{PACKAGE}: Initial load')
        """initial loading"""
    import_succeeded = True
except ModuleNotFoundError as e:
    print(f'{PACKAGE}: ModuleNotFoundError occurred when trying to enable add-on.')
    print(e)
except Exception as e:
    print(f'{PACKAGE}: Unexpected Exception occurred when trying to enable add-on.')
    print(e)

"""
IMPORT ORDER

### USER INTERFACE

->  from _blender.interface import
        install_dependencies,
        ui_registration
    import m_CONST
importlib.reload(install_dependencies)
importlib.reload(log)
importlib.reload(stream_detection_operator)

### BPY RIGGING
importlib.reload(m_V)
importlib.reload(constraints)
importlib.reload(m_CONST)
importlib.reload(objects)
importlib.reload(abs_rigging)
importlib.reload(limb_drivers)
importlib.reload(log)

### BRIDGE
importlib.reload(objects)
importlib.reload(log)
importlib.reload(m_CONST)
importlib.reload(m_V)
importlib.reload(abs_assignment)

### DETECTION
importlib.reload(pose_drivers)
importlib.reload(abstract_detector)
importlib.reload(abstract_detector)
importlib.reload(pose_drivers)
importlib.reload(hand_drivers)
importlib.reload(abstract_detector)
importlib.reload(face_drivers)
importlib.reload(abstract_detector)


"""
