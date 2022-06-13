'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import subprocess
import sys

import bpy

from . import ui_registration
from ..utils import dependencies
from ... import cgt_imports


class PREFERENCES_OT_CGT_install_dependencies_button(bpy.types.Operator):
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
        # try to install dependencies
        try:
            dependencies.install_pip()
            # dependencies.update_pip()
            for dependency in dependencies.required_dependencies:
                dependencies.install_and_import_module(dependency)
        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))
            return {"CANCELLED"}

        # register user interface after installing dependencies
        ui_registration.register_user_interface()
        # TODO: update UI without reimporting
        cgt_imports.manage_imports(reload=True)
        return {"FINISHED"}


class PREFERENCES_OT_CGT_uninstall_dependencies_button(bpy.types.Operator):
    bl_idname = "button.cgt_uninstall_dependencies"
    if sys.platform == "win32":
        bl_label = "Uninstall Dependencies and Shutdown Blender"
    else:
        bl_label = "Uninstall Dependencies"
    bl_description = ("Uninstalls Mediapipe, OpenCV, Google Protobuffers")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        # Deactivate install button when dependencies are not installed
        return dependencies.dependencies_installed

    def execute(self, context):
        dependencies.dependencies_installed = False
        # uninstall dependencies or move them to custom trash folder
        # on windows to remove files on app start
        for dependency in dependencies.required_dependencies:
            try:
                uninstalled = dependencies.uninstall_dependency(dependency)
                if not uninstalled:
                    dependencies.dependencies_installed = True
            except (subprocess.CalledProcessError, ImportError) as err:
                dependencies.dependencies_installed = True
                self.report({"ERROR"}, str(err))

        if dependencies.dependencies_installed is False:
            # unregister function checks for dependencies
            ui_registration.unregister_ui_panels()

        if sys.platform == "win32":
            # todo combine / remove?
            print("Attempt to shutdown Blender.")
            import time
            time.sleep(3)
            bpy.ops.wm.quit_blender()
        else:
            # TODO: update UI without reimporting as soon pip gets fixed
            cgt_imports.manage_imports(reload=True)

        return {"FINISHED"}
