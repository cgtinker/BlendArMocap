import importlib
import subprocess

import bpy
from bpy.props import PointerProperty

from blender.interface import Properties
from blender.interface import install_dependencies, Registration

importlib.reload(install_dependencies)


class EXAMPLE_OT_install_dependencies(bpy.types.Operator):
    bl_idname = "example.install_dependencies"
    bl_label = "Install dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is required. Blender may have to be started with "
                      "elevated permissions in order to install the package")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate when dependencies have been installed
        return not dependencies_installed

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

        global dependencies_installed
        dependencies_installed = True

        # Register the panels, operators, etc. since dependencies are installed
        for cls in Registration.classes:
            bpy.utils.register_class(cls)

        bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)

        return {"FINISHED"}


class EXAMPLE_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.operator(EXAMPLE_OT_install_dependencies.bl_idname, icon="CONSOLE")
