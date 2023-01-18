import bpy
from pathlib import Path
import shutil
import logging


class OT_CGT_Import_Transfer_Config(bpy.types.Operator):
    """ Imports transfer configuration file."""
    bl_idname = "wm.import_rig_transfer_config"
    bl_label = "Import BlendArMocap Transfer Configuration"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json;", options={'HIDDEN'}, )
    filepath: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', default="*.json;",
                                       options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        layout = self.layout

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        def current_files():
            path = Path(__file__).parent / 'data'
            files = [x for x in path.glob('**/*') if x.is_file()]
            if len(files) == 0:
                return ["None"]
            return [str(x.name) for x in files]

        from_path = Path(self.filepath)
        name = from_path.name

        if name in current_files():
            self.report({'ERROR'}, "Overwriting is not supported. "
                                   "Consider to change the configuration filename. ")
            return {'CANCELLED'}

        to_path = Path(__file__).parent / "data" / name
        shutil.copy(str(from_path), str(to_path))
        self.report({'INFO'}, f"Import Configuration from {self.filepath} to {str(to_path)}")
        return {'FINISHED'}


class OT_CGT_Export_Transfer_Config(bpy.types.Operator):
    """ Export transfer configuration file. """
    bl_idname = "wm.export_rig_transfer_config"
    bl_label = "Export BlendArMocap Transfer Configuration"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json;", options={'HIDDEN'}, )
    filepath: bpy.props.StringProperty(maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        layout = self.layout
        user = context.scene.cgtinker_transfer  # noqa
        row = layout.row(align=True)
        row.prop(user, "transfer_types", text="Export Configuration")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        user = context.scene.cgtinker_transfer  # noqa
        config = user.transfer_types
        config += '.json'

        from_path = Path(__file__).parent / "data" / config
        to_path = Path(self.directory) / config

        shutil.copy(str(from_path), str(to_path))
        self.report({'INFO'}, f"Exported Configuration {str(from_path)} to {str(to_path)}")
        return {'FINISHED'}


def import_config_button(self, context):
    self.layout.operator(OT_CGT_Import_Transfer_Config.bl_idname, text="BlendArMocap Config (.json)")


def export_config_button(self, context):
    self.layout.operator(OT_CGT_Export_Transfer_Config.bl_idname, text="BlendArMocap Config (.json)")


classes = [
    OT_CGT_Export_Transfer_Config,
    OT_CGT_Import_Transfer_Config
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(import_config_button)
    bpy.types.TOPBAR_MT_file_export.append(export_config_button)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(export_config_button)
    bpy.types.TOPBAR_MT_file_import.remove(import_config_button)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
