import subprocess
import bpy

from ..cgt_core.cgt_interface import cgt_core_panel
from ..cgt_mediapipe import cgt_dependencies


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
                success = cgt_dependencies.install_dependency(self, dependency)
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


def draw(self, context):
    layout = self.layout

    draw_dependencies(layout)
    if all(cgt_dependencies.dependencies_installed):
        draw_camera_settings(context, layout)


def draw_dependencies(layout):

    """ Dependency layout for user preferences. """
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

    dependency_box.row().separator()
    dependency_box.row().label(text="Make sure to have elevated privileges.")
    # install dependencies button
    dependency_box.row().operator(PREFERENCES_OT_CGT_install_dependencies_button.bl_idname, icon="CONSOLE")
    dependency_box.row().operator(PREFERENCES_OT_CGT_uninstall_dependencies_button.bl_idname, icon="ERROR")


def draw_camera_settings(context, layout):
    if cgt_dependencies.dependencies_installed:
        s_box = layout.box()
        user = context.scene.cgtinker_mediapipe  # noqa
        s_box.label(text="Camera Settings")
        s_box.row().prop(user, "enum_stream_dim")
        s_box.row().prop(user, "enum_stream_type")


classes = [
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
