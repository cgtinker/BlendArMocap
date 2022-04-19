import bpy

from ... import cgt_naming
from . import pref_operators


class BLENDARMOCAP_preferences(bpy.types.AddonPreferences):
    bl_idname = cgt_naming.PACKAGE

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe # noqa

        layout = self.layout
        d_box = self.layout.box()
        d_box.label(text='Dependencies')
        d_box.row().operator(pref_operators.PREFERENCES_OT_install_dependencies_button.bl_idname, icon="CONSOLE")

        if user.pvb:
            s_box = self.layout.box()
            s_box.label(text='Camera Settings')
            s_box.row().prop(user, "enum_stream_dim")
            s_box.row().prop(user, "enum_stream_type")
