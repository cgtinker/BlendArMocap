import importlib
import sys

PACKAGE: str = ''
reload_list: list = None
module_type: str = ''

load_order: dict = {
    'init':  [
        'cgt_naming',
        'cgt_blender.interface.ui_registration',
        'cgt_blender.cgt_rig',
        'cgt_blender.input_manager',
        'cgt_blender.interface',
        'cgt_blender'
    ],
    'core':  [
        'cgt_utils.open_cv',
        'cgt_utils',
        'cgt_detection',
        'cgt_bridge.face_drivers',
        'cgt_bridge',
    ],
    'debug': [
        'cgt_naming',
        'cgt_blender',
        'cgt_bridge',
        'cgt_detection',
    ]
}


def get_loaded_modules():
    prefix = PACKAGE
    return [name for name in sys.modules if name.startswith(prefix)]


def reload_modules():
    fixed_modules = set(reload_list)
    for name in get_loaded_modules():
        if name not in fixed_modules:
            print("NAMING CONFLICT WHILE INITIALIZATION:", name)
    for name in reload_list:
        importlib.reload(sys.modules[name])


def load_initial_modules():
    print("load initial modules:\n", load_order[module_type])
    load_list = [PACKAGE + '.' + name for name in load_order[module_type]]
    for i, name in enumerate(load_list):
        print("attempt to load:", i, name, "...")
        importlib.import_module(name)
    return load_list


def execute():
    if PACKAGE in locals():
        print(f'{PACKAGE}: Reloading package...')
        reload_modules()
    else:
        print(f'{PACKAGE}: Initial package loading... ')
        load_list = load_initial_modules()
        print("\nload_list:", load_list)
    reload_list = load_order[module_type] = get_loaded_modules()
    print("\nreload_list:", reload_list)

    if module_type == 'debug':
        for module_name in reload_list:
            module = importlib.import_module(module_name)
            importlib.reload(module)
