import subprocess
import bpy

from ..cgt_core.cgt_interface import cgt_core_panel
from ..cgt_mediapipe import cgt_dependencies
from ..cgt_core.cgt_utils import cgt_user_prefs


class PREFERENCES_OT_CGT_install_dependencies_button(bpy.types.Operator):
    bl_idname = "button.cgt_install_dependencies"
    bl_label = "Install dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is required. Blender may have to be started with "
                      "elevated permissions in order to install the package")
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        return not all(cgt_dependencies.dependencies_installed)

    def execute(self, context):
        try:
            cgt_dependencies.ensure_pip(self)
            for i, dependency in enumerate(cgt_dependencies.required_dependencies):
                if cgt_dependencies.dependencies_installed[i]:
                    continue
                user = context.scene.cgtinker_mediapipe  # noqa
                success = cgt_dependencies.install_dependency(self, dependency, user.local_user)
                cgt_dependencies.dependencies_installed[i] = success

        except (subprocess.CalledProcessError, ImportError) as err:
            self.report({"ERROR"}, str(err))
            return {"CANCELLED"}
        return {"FINISHED"}


class PREFERENCES_OT_CGT_uninstall_dependencies_button(bpy.types.Operator):
    bl_idname = "button.cgt_uninstall_dependencies"
    bl_label = "Uninstall dependencies and shutdown"
    bl_description = "Removes installed dependencies from site-packages" \
                     "and deletes them on start up."
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(self, context):
        return any(cgt_dependencies.dependencies_installed)

    def execute(self, context):
        for i, dependency in enumerate(cgt_dependencies.required_dependencies):
            if not cgt_dependencies.is_installed(dependency):
                continue
            success = cgt_dependencies.uninstall_dependency(self, dependency)
            cgt_dependencies.dependencies_installed[i] = success

        import time
        time.sleep(1)
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


class PREFERENCES_OT_CGT_save_preferences(bpy.types.Operator):
    bl_idname = "button.cgt_save_preferences"
    bl_label = "Save Preferences"
    bl_description = "Save BlendArMocaps User Preferences"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        from .cgt_mp_registration import MP_ATTRS
        user = bpy.context.scene.cgtinker_mediapipe  # noqa
        cgt_user_prefs.set_prefs(**{attr: getattr(user, attr, default) for attr, default in MP_ATTRS.items()})
        self.report({'INFO'}, "Saved user preferences.")
        return {"FINISHED"}


def draw(self, context):

    """ Dependency layout for user preferences. """
    layout = self.layout
    user = context.scene.cgtinker_mediapipe  # noqa

    # dependency box
    dependency_box = layout.box()
    dependency_box.label(text="Mediapipe Dependencies")

    def draw_dependency(dependency, dependency_box):
        """ Draws package name, version, path and if a dependency has been installed. """
        _d_box = dependency_box.box()
        box_split = _d_box.split()
        cols = [box_split.column(align=False) for _ in range(4)]
        cols[3].label(text=f"{cgt_dependencies.is_installed(dependency)}")
        if not cgt_dependencies.is_installed(dependency):
            cols[0].label(text=f"{dependency.name}")
            cols[1].label(text=f"NaN")
            cols[2].label(text=f"NaN")

        else:
            version, path = cgt_dependencies.get_package_info(dependency)
            cols[0].label(text=f"{dependency.name}")
            cols[1].label(text=f"{version}")
            cols[2].label(text=f"{path}")

    # pip headers
    pip_headers = dependency_box.split()
    for name in ["Installer", "Version", "Path", "Installed"]:
        col = pip_headers.column()
        col.label(text=name)

    # draw dependencies individually
    draw_dependency(cgt_dependencies.Dependency("pip", "pip", "pip", None), dependency_box)
    dependency_box.row().separator()

    dependency_header = dependency_box.row()
    dependency_header.label(text="Dependencies")

    # dependency headers
    headers = dependency_box.split()
    for name in ["Module", "Version", "Path", "Installed"]:
        col = headers.column()
        col.label(text=name)
    for m_dependency in cgt_dependencies.required_dependencies:
        draw_dependency(m_dependency, dependency_box)

    # user settings
    dependency_box.row().separator()
    settings_box = layout.box()
    if all(cgt_dependencies.dependencies_installed):
        # cam settings
        settings_box.label(text="Camera Settings")
        settings_box.row().prop(user, "enum_stream_dim")
        settings_box.row().prop(user, "enum_stream_type")
        settings_box.row().separator()
        settings_box.label(text="Dependency Settings")
    else:
        # install dependencies button
        settings_box.label(text="Dependency Settings")
        settings_box.row().label(text="Make sure to have elevated privileges.")
        settings_box.row().operator(PREFERENCES_OT_CGT_install_dependencies_button.bl_idname, icon="CONSOLE")
    deps_col = settings_box.row()
    deps_col.row(align=True).prop(user, "local_user")
    deps_col.row().operator(PREFERENCES_OT_CGT_save_preferences.bl_idname)


classes = [
    PREFERENCES_OT_CGT_save_preferences,
    PREFERENCES_OT_CGT_install_dependencies_button,
    PREFERENCES_OT_CGT_uninstall_dependencies_button
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    cgt_core_panel.addon_prefs.add(draw)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
