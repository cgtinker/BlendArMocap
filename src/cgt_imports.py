import importlib
import sys
from pathlib import Path

"""
This makes sure all modules are reloaded from new files, when the addon is removed and a new version is installed in the same session,
or when Blender's 'Reload Scripts' operator is run manually.
"""

SUB_DIRS = ['cgt_blender', 'cgt_bridge', 'cgt_detection', 'cgt_utils']
INIT_MODULES = [
    '.cgt_naming',
    '.cgt_imports',
    '.cgt_blender.interface.ui_properties',
    '.cgt_blender.interface.ui_registration',
    '.cgt_blender.input_manager',
    '.cgt_blender.interface',
    '.cgt_blender.utils.install_dependencies',
]

FILE = Path(__file__)
PARENT = FILE.parent
PACKAGE = PARENT.name


def import_module(module):
    importlib.import_module(f"{PACKAGE}{module}")


def reload_module(module):
    importlib.reload(sys.modules[f"{PACKAGE}{module}"])


def get_reload_list(sub_dirs):
    reload_list = []

    for sub_dir in sub_dirs:
        files = [p for p in sub_dir.rglob("*.py") if p.stem != '__init__']
        for file in files:
            parents = get_parents(file, [])
            imp_path = ""
            for parent in reversed(parents):
                imp_path += f".{parent}"
            imp_path += f".{file.stem}"
            reload_list.append(imp_path)
    return reload_list


def get_parents(file: Path, parents: list):
    if file.parent.name != PACKAGE:
        parents.append(file.parent.name)
        get_parents(file.parent, parents)
    return parents


def manage_imports(reload=False):
    for module in INIT_MODULES:
        import_module(module)

    from src.cgt_blender.utils import install_dependencies
    print("DEPENDENCIES INSTALLED:", install_dependencies.dependencies_installed)

    if install_dependencies.dependencies_installed is True:
        print(f"Attempt to reload {PACKAGE}")
        sub_dirs = [PARENT / sub_dir for sub_dir in SUB_DIRS]
        reload_list = get_reload_list(sub_dirs)

        for module in reload_list:
            if reload is True:
                import_module(module)
                reload_module(module)
            else:
                import_module(module)
        print(f"Reloaded {PACKAGE} successfully")


if __name__ == '__main__':
    addons_folder = str(PARENT.parent)
    sys.path.append(addons_folder)

    # reload modules besides bpy
    sub_dirs = [PARENT / sub_dir for sub_dir in SUB_DIRS[1:]]
    reload_list = get_reload_list(sub_dirs)
    for module in reload_list:
        print(f"importing {module}...")
        import_module(module)
