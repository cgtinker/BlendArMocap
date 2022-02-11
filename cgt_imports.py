import importlib
import os
import sys

"""
This makes sure all modules are reloaded from new files, when the addon is removed and a new version is installed in the same session,
or when Blender's 'Reload Scripts' operator is run manually.
"""
SUB_DIRS = ['cgt_blender', 'cgt_bridge', 'cgt_detection', 'cgt_utils']
INIT_MODULES = [
    'cgt_naming',
    'cgt_imports',
    'cgt_blender.interface.ui_properties',
    'cgt_blender.interface.ui_registration',
    'cgt_blender.input_manager',
    'cgt_blender.interface',
    'cgt_blender.utils.install_dependencies',
]

PACKAGE = os.path.basename(os.path.dirname(__file__))


def import_module(module):
    print(f"importing {PACKAGE}.{module}...")
    importlib.import_module(f"{PACKAGE}.{module}")


def reload_module(module):
    print(f"reloading {PACKAGE}.{module}...")
    importlib.reload(sys.modules[f"{PACKAGE}.{module}"])


def get_reload_list(sub_dirs):
    reload_list = []

    for sub_dir in sub_dirs:
        for root, sub_dir, files in os.walk(sub_dir):
            # get all python modules files for the import
            sub_path = root.replace(os.path.dirname(__file__) + "/", "")
            sub_path = sub_path.replace("/", ".")
            modules = [f"{file.replace('.py', '')}" for file in files
                       if file.endswith('.py') if file != '__init__.py']

            for module in modules:
                m_module = f"{sub_path}.{module}"
                reload_list.append(m_module)

    return reload_list


# first reload the required modules to activate the UI
def manage_imports(reload=False):
    for module in INIT_MODULES:
        import_module(module)

    from .cgt_blender.utils import install_dependencies
    print("DEPENDENCIES INSTALLED:", install_dependencies.dependencies_installed)

    if install_dependencies.dependencies_installed is True:
        print(f"Attempt to reload {PACKAGE}")
        package = os.path.dirname(__file__)
        sub_dirs = [os.path.join(package, sub_dir) for sub_dir in SUB_DIRS]
        reload_list = get_reload_list(sub_dirs)

        for module in reload_list:
            if reload is True:
                reload_module(module)
            else:
                import_module(module)
        print(f"Reloaded {PACKAGE} successfully")
