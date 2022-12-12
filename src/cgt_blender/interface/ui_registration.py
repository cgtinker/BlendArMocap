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

from . import ui_properties, cgt_panels, pref_operators, pref_panels, ui_operators, cgt_main_panel


classes = (
    pref_operators.PREFERENCES_OT_CGT_install_dependencies_button,
    pref_operators.PREFERENCES_OT_CGT_uninstall_dependencies_button,
    pref_panels.BLENDARMOCAP_CGT_preferences,

    ui_properties.CGTProperties,

    # ui_operators.UI_CGT_transfer_anim_button,
    # ui_operators.UI_CGT_toggle_drivers_button,
    # ui_operators.UI_CGT_smooth_empties_in_col,
    # ui_operators.WM_CGT_modal_detection_operator,
    # ui_operators.WM_CGT_modal_connection_listener_operator,
    # cgt_panels.UI_PT_Detection_Panel,
    # cgt_panels.UI_PT_CGT_Transfer_Panel
    # ui_panels.UI_PT_RemappingPanel
)


def register():
    for _class in classes:
        register_class(_class)

    ui_operators.register()
    cgt_main_panel.register()
    cgt_panels.register()
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CGTProperties)


def unregister():
    for cls in classes:
        unregister_class(cls)

    cgt_panels.unregister()
    cgt_main_panel.unregister()
    ui_operators.unregister()
