import importlib
import subprocess

import bpy

from blender.interface import install_dependencies, Registration

importlib.reload(install_dependencies)


class PREFERENCES_OT_install_dependencies_button(bpy.types.Operator):
    bl_idname = "button.install_dependencies"
    bl_label = "Install dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is required. Blender may have to be started with "
                      "elevated permissions in order to install the package")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate when dependencies have been installed
        return not install_dependencies.dependencies_installed

    def execute(self, context):
        try:
            install_dependencies.install_pip()
            for dependency in install_dependencies.dependencies:
                install_dependencies.install_and_import_module(module_name=dependency.module,
                                                               package_name=dependency.package,
                                                               global_name=dependency.name)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))
            return {"CANCELLED"}

        install_dependencies.dependencies_installed = True
        Registration.register_user_interface()

        return {"FINISHED"}


class EXAMPLE_preferences(bpy.types.AddonPreferences):
    # TODO: fix package name
    bl_idname = "mediapipetests"

    def draw(self, context):
        layout = self.layout
        layout.operator(PREFERENCES_OT_install_dependencies_button.bl_idname, icon="CONSOLE")
