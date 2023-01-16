import bpy


class UI_PT_CGT_Properties_Freemocap(bpy.types.PropertyGroup):
    freemocap_session_path: bpy.props.StringProperty(
        name="Path",
        default="/Users/Scylla/Downloads/sesh_2022-09-19_16_16_50_in_class_jsm/",
        description="Directory path to freemocap session.",
        options={'HIDDEN'},
        maxlen=1024,
        subtype='DIR_PATH'
    )
    modal_active: bpy.props.BoolProperty(default=False)
    load_raw: bpy.props.BoolProperty(
        default=False, description="Loads raw session data - may not be transferred to rigs.")
    quickload: bpy.props.BoolProperty(
        default=False, description="Quickload session folder. (Freezes Blender)")


class UI_PT_CGT_Panel_Freemocap(bpy.types.Panel):
    bl_label = "Freemocap"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def quickload_session_folder(self, user):
        if user.modal_active:
            self.layout.row().operator("wm.cgt_quickload_freemocap_operator", text="Stop Import", icon='CANCEL')
        else:
            self.layout.row().operator("wm.cgt_quickload_freemocap_operator", text="Quickload Session Folder", icon='IMPORT')

    def load_session_folder(self, user):
        if user.modal_active:
            self.layout.row().operator("wm.cgt_load_freemocap_operator", text="Stop Import", icon='CANCEL')
        else:
            self.layout.row().operator("wm.cgt_load_freemocap_operator", text="Load Session Folder", icon='IMPORT')

    def draw(self, context):
        layout = self.layout

        user = context.scene.cgtinker_freemocap  # noqa
        layout.row().prop(user, "freemocap_session_path")
        if not user.quickload:
            self.load_session_folder(user)
        else:
            self.quickload_session_folder(user)

        self.layout.row().operator("wm.fmc_load_synchronized_videos", text="Load synchronized videos", icon='IMAGE_PLANE')
        row = layout.row()
        row.column(align=True).prop(user, "quickload", text="Quickload", toggle=True)
        if user.quickload:
            row.column(align=True).prop(user, "load_raw", text="Raw", toggle=True)
        # layout.separator()
        # layout.row().operator("wm.fmc_bind_freemocap_data_to_skeleton", text="Bind to rig (Preview)")


classes = [
    UI_PT_CGT_Properties_Freemocap,
    UI_PT_CGT_Panel_Freemocap,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_freemocap = bpy.props.PointerProperty(type=UI_PT_CGT_Properties_Freemocap)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cgtinker_freemocap # noqa


if __name__ == '__main__':
    try:
        unregister()
    except RuntimeError:
        pass

    register()
