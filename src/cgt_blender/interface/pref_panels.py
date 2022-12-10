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

import bpy
from . import pref_operators
from ..utils import dependencies
from ... import cgt_naming


class BLENDARMOCAP_CGT_preferences(bpy.types.AddonPreferences):
    bl_idname = cgt_naming.PACKAGE
    update = True  # used to check dependency status just once

    def draw(self, context):
        layout = self.layout

        user = context.scene.m_cgtinker_mediapipe  # noqa
        layout.prop(user, "legacy_features_bool")

        if self.update and user.legacy_features_bool:
            self.draw_dependencies(layout)
            self.draw_camera_settings(context, layout)
            self.update = False

    def draw_dependencies(self, layout):
        """ Dependency layout for user preferences. """
        # dependency box
        dependency_box = layout.box()
        dependency_box.label(text="Essential")

        # pip headers
        pip_head = dependency_box.split()
        for name in ["Installer", "Version", "Path", "Installed"]:
            col = pip_head.column()
            col.label(text=name)

        # draw dependencies individually
        self.draw_dependency(dependencies.Dependency("pip", "pip", "pip", "pip"), dependency_box)
        dependency_box.row().separator()

        dependency_header = dependency_box.row()
        dependency_header.label(text="Dependencies")

        # dependency headers
        headers = dependency_box.split()
        for name in ["Module", "Version", "Path", "Installed"]:
            col = headers.column()
            col.label(text=name)
        for m_dependency in dependencies.required_dependencies:
            self.draw_dependency(m_dependency, dependency_box)

        dependency_box.row().separator()
        dependency_box.row().label(text="Make sure to have elevated privileges.")
        # install dependencies button
        dependency_box.row().operator(
            pref_operators.PREFERENCES_OT_CGT_install_dependencies_button.bl_idname  #, icon="CONSOLE"
        )

        dependency_box.row().operator(
            pref_operators.PREFERENCES_OT_CGT_uninstall_dependencies_button.bl_idname  #, icon="ERROR"
        )

    def draw_dependency(self, m_dependency, dependency_box):
        """ Draws package name, version, path and if a dependency has been installed. """
        _d_box = dependency_box.box()
        box_split = _d_box.split()
        cols = [box_split.column(align=False) for _ in range(4)]
        updated_dependency = dependencies.dependency_naming(m_dependency)

        cols[3].label(text=f"{dependencies.is_package_installed(updated_dependency)}")
        if not dependencies.is_package_installed(updated_dependency):
            cols[0].label(text=f"{updated_dependency.name}")
            cols[1].label(text=f"NaN")
            cols[2].label(text=f"NaN")

        else:
            _version, _path = dependencies.get_package_info(updated_dependency)
            cols[0].label(text=f"{updated_dependency.name}")
            cols[1].label(text=f"{_version}")
            cols[2].label(text=f"{_path}")

    def draw_camera_settings(self, context, layout):
        if dependencies.dependencies_installed:
            s_box = layout.box()
            user = context.scene.m_cgtinker_mediapipe  # noqa
            s_box.label(text="Camera Settings")
            s_box.row().prop(user, "enum_stream_dim")
            s_box.row().prop(user, "enum_stream_type")

