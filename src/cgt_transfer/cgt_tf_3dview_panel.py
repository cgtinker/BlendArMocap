import bpy
from pathlib import Path
from bpy.types import Panel
from ..cgt_core.cgt_interface import cgt_core_panel

from bpy.props import PointerProperty


class CgtRigifyTransferProperties(bpy.types.PropertyGroup):
    advanced_features: bpy.props.BoolProperty(default=True)
    save_object_properties_bool: bpy.props.BoolProperty(
        default=False,
        description="Save data for transferring animation data (located in the object constraint properties) toggle."
    )
    delete_object_properties_bool: bpy.props.BoolProperty(
        default=False,
        description="Delete a configuration file toggle."
    )
    save_object_properties_name: bpy.props.StringProperty(
        default="",
        description="Insert name for the new mocap transfer configuration file."
    )

    def is_armature(self, object):
        if object.type == 'ARMATURE':
            return True
        return False

    selected_rig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        description="Select an armature for animation transfer.",
        name="Armature",
        poll=is_armature)

    def json_files(self, context):
        path = Path(__file__).parent / 'data'

        files = [x for x in path.glob('**/*') if x.is_file()]
        if len(files) == 0:
            return [('None', 'None', "")]
        return [(str(x.name)[:-5], str(x.name)[:-5], "") for x in files]

    transfer_types: bpy.props.EnumProperty(
        name="Target Type",
        items=json_files
    )

    def cgt_collection_poll(self, col):
        return col.name.startswith('cgt_')

    selected_driver_collection: bpy.props.PointerProperty(
        name="",
        type=bpy.types.Collection,
        description="Select a collection of Divers.",
        poll=cgt_collection_poll
    )


class PT_CGT_Main_Transfer(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Transfer"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_idname = "UI_PT_Transfer_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        user = context.scene.cgtinker_transfer  # noqa
        layout = self.layout

        row = layout.row(align=True)
        row.prop_search(data=user, property="selected_rig", search_data=bpy.data,
                        search_property="objects", text="Armature", icon="ARMATURE_DATA")
        row.label(icon='BLANK1')

        row = layout.row(align=True)
        row.prop_search(data=user, property="selected_driver_collection", search_data=bpy.data,
                        search_property="collections", text="Drivers")
        row.label(icon='BLANK1')

        row = layout.row(align=True)
        row.prop(user, "transfer_types", text="Transfer Type")

        if not user.advanced_features:
            row.label(icon='BLANK1')
            row = layout.row(align=True)
            row.use_property_decorate = False
            row.operator("button.cgt_object_apply_properties", text="Transfer Animation", icon="DRIVER")
            return

        row.prop(user, "delete_object_properties_bool", text="", icon='TRASH')

        # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=True)
        # col = flow.column(align=True)
        row = layout.row(align=True)
        col = row.column(align=True)

        if user.delete_object_properties_bool:
            row = col.row(align=True)
            row.use_property_decorate = False
            row.label(text="Deletion is permanent. Proceed?")
            row.operator("button.cgt_object_delete_properties", text="", icon='CHECKMARK')
            row.prop(user, "delete_object_properties_bool", text="", icon='CANCEL', invert_checkbox=True)
            col.separator()

        row = col.row(align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.operator("button.cgt_object_load_properties", text="Load", icon='FILE_TICK')
        sub.prop(user, "save_object_properties_bool", text="Save Config", icon='FILE_NEW')

        if user.save_object_properties_bool:
            row = col.row(align=True)
            row.use_property_decorate = False
            row.prop(user, "save_object_properties_name", text="")
            row.operator("button.cgt_object_save_properties", text="", icon='CHECKMARK')
            row.prop(user, "save_object_properties_bool", text="", toggle=True, icon='CANCEL', invert_checkbox=True)

        row = col.row(align=True)
        row.use_property_decorate = False
        row.operator("button.cgt_object_apply_properties", text="Transfer Animation", icon="DRIVER")


class PT_CGT_Advanced_Transfer(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Advanced"
    bl_parent_id = "UI_PT_Transfer_Panel"
    bl_idname = "UI_PT_CGT_Transfer_Tools"

    def draw(self, context):
        user = context.scene.cgtinker_transfer  # noqa
        layout = self.layout
        row = layout.row(align=True)
        row.prop(user, "advanced_features", text="Use Advanced Features", toggle=True)


classes = [
    PT_CGT_Main_Transfer,
    CgtRigifyTransferProperties,
    # PT_CGT_Advanced_Transfer,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_transfer = PointerProperty(type=CgtRigifyTransferProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cgtinker_transfer
