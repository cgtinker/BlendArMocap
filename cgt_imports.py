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
    load_list = [PACKAGE + '.' + name for name in load_order[module_type]]
    for i, name in enumerate(load_list):
        importlib.import_module(name)
    return load_list


def execute():
    if 'reload_list' in locals():
        print("IS IN LOCALS")
    else:
        print("NOT IN LOCALS")
    if PACKAGE in locals():
        print(f'{PACKAGE}: Reloading package...')
        reload_modules()
    else:
        print(f'{PACKAGE}: Initial package loading... ')
        load_list = load_initial_modules()
    reload_list = load_order[module_type] = get_loaded_modules()
    for module_name in reload_list:
        module = importlib.import_module(module_name)
        importlib.reload(module)
    if module_type == 'debug':
        print("\nload list:", load_list)
        print("\nreload_list", reload_list)
    print(locals())
