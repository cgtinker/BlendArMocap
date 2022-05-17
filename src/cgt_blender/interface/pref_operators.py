import subprocess

import bpy

from . import ui_registration
from ..utils import dependencies
from ... import cgt_imports


class PREFERENCES_OT_install_dependencies_button(bpy.types.Operator):
    bl_idname = "button.cgt_install_dependencies"
    bl_label = "Install dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is required. Blender may have to be started with "
                      "elevated permissions in order to install the package")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate install button when dependencies have been installed
        return not dependencies.dependencies_installed

    def execute(self, context):
        try:
            # try to install dependencies
            dependencies.install_pip()
            dependencies.update_pip()
            for dependency in dependencies.required_dependencies:
                dependencies.install_and_import_module(dependency)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))
            return {"CANCELLED"}

        # register user interface after installing dependencies
        dependencies.dependencies_installed = True
        ui_registration.register_user_interface()
        cgt_imports.manage_imports(reload=True)
        return {"FINISHED"}


class PREFERENCES_OT_uninstall_dependencies_button(bpy.types.Operator):
    bl_idname = "button.cgt_uninstall_dependencies"
    bl_label = "Uninstall Dependencies"
    bl_description = ("Uninstalls Mediapipe and OpenCV")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate install button when dependencies have been installed
        return dependencies.dependencies_installed

    def execute(self, context):
        try:
            # try to uninstall dependencies
            for dependency in dependencies.required_dependencies:
                dependencies.uninstall_dependency(dependency)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))

        # register user interface after installing dependencies
        dependencies.dependencies_installed = False

        # force pref panel to redraw
        from . import pref_panels
        pref_panels.redraw_preferences()
        dependencies.dependencies_installed = False

        return {"FINISHED"}
