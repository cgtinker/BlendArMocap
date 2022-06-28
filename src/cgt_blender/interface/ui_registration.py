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
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from . import ui_properties, ui_panels, pref_operators, pref_panels, ui_operators
from ..utils import dependencies


def get_classes():
    # getting classes to avoid loading possibly unavailable packages
    classes = (
        ui_properties.CGTProperties,

        ui_operators.UI_CGT_transfer_anim_button,
        ui_operators.UI_CGT_toggle_drivers_button,
        ui_operators.WM_CGT_modal_detection_operator,
        ui_operators.WM_FMC_bind_freemocap_data_to_skeleton,
        ui_operators.WM_FMC_load_synchronized_videos,
        ui_panels.UI_PT_CGT_main_panel,
        # ui_panels.UI_PT_RemappingPanel
    )
    return classes


def get_preferences():
    preference_classes = (pref_operators.PREFERENCES_OT_CGT_install_dependencies_button,
                          pref_operators.PREFERENCES_OT_CGT_uninstall_dependencies_button,
                          pref_panels.BLENDARMOCAP_CGT_preferences,
                          ui_panels.UI_PT_CGT_warning_panel)
    return preference_classes


def register():
    print('Registing BlendArMocap\n')

    for m_class in get_preferences():
        # print(m_class)
        register_class(m_class)

    try:
        print('Try to access dependencies')
        for dependency in dependencies.required_dependencies:
            pkg_info = dependencies.get_package_info(dependency)
            print(dependency.module, pkg_info)

        if dependencies.dependencies_installed:
            register_user_interface()

    except ModuleNotFoundError:
        # Don't register other panels, ui_operators etc.
        print('REGISTRATION FAILED: REQUIRED MODULE NOT FOUND')
        return


def register_user_interface():
    for cls in get_classes():
        try:
            register_class(cls)
        except ValueError:
            print("Class has already been registered:", cls)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CGTProperties)


def unregister():
    print("Unregister BlendArMocap")
    for cls in get_preferences():
        try:
            unregister_class(cls)
        except RuntimeError:
            # Class may not be registered
            pass

    if dependencies.dependencies_installed:
        unregister_ui_panels()


def unregister_ui_panels():
    classes = get_classes()
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except RuntimeError:
            print("Class may not be registered:", cls)
    try:
        del bpy.types.Scene.m_cgtinker_mediapipe  # noqa
    except AttributeError:
        # hasn't been registered due to missing dependencies
        pass


def manual_unregistration():
    print("MANUAL UNREGISTER")
    classes = get_classes()
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.m_cgtinker_mediapipe # noqa


def manual_test_registration():
    print("MANUAL REGISTER")
    for cls in get_classes():
        register_class(cls)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CGTProperties)
