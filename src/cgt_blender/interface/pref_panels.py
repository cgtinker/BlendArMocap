import bpy

from . import pref_operators
from ..utils import dependencies
from ... import cgt_naming
from bpy.utils import register_class, unregister_class


class BLENDARMOCAP_preferences(bpy.types.AddonPreferences):
    bl_idname = cgt_naming.PACKAGE

    def draw(self, context):
        layout = self.layout
        self.draw_dependencies(layout)

        # only if dependencies installed
        if dependencies.dependencies_installed:
            s_box = layout.box()
            user = context.scene.m_cgtinker_mediapipe  # noqa
            s_box.label(text="Camera Settings")
            s_box.row().prop(user, "enum_stream_dim")
            s_box.row().prop(user, "enum_stream_type")

    def draw_dependencies(self, layout):
        # dependency box
        dependency_box = layout.box()
        dependency_box.label(text="Dependencies")

        # pip headers
        pip_head = dependency_box.split()
        for name in ["Installer", "Version", "Path", "Installed"]:
            col = pip_head.column()
            col.label(text=name)

        # draw dependencies individually
        self.draw_dependency(dependencies.Dependency("pip", "pip", "pip", "pip"), dependency_box)
        dependency_box.row().separator()

        # dependency headers
        headers = dependency_box.split()
        for name in ["Module", "Version", "Path", "Installed"]:
            col = headers.column()
            col.label(text=name)
        for m_dependency in dependencies.required_dependencies:
            self.draw_dependency(m_dependency, dependency_box)

        dependency_box.row().separator()

        # install dependencies button
        dependency_box.row().operator(
            pref_operators.PREFERENCES_OT_install_dependencies_button.bl_idname, icon="CONSOLE"
        )

        dependency_box.row().operator(
            pref_operators.PREFERENCES_OT_uninstall_dependencies_button.bl_idname, icon="CONSOLE"
        )

    def draw_dependency(self, m_dependency, dependency_box):
        _d_box = dependency_box.box()
        box_split = _d_box.split()
        cols = [box_split.column(align=False) for _ in range(4)]
        updated_dependency = dependencies.dependency_naming(m_dependency)

        if not dependencies.is_package_installed(m_dependency):
            cols[0].label(text=f"{updated_dependency.package}")
            cols[1].label(text=f"NaN")
            cols[2].label(text=f"NaN")
            cols[3].label(text=f"{False}")

        else:
            _version, _path = dependencies.get_package_info(m_dependency.pkg)
            cols[0].label(text=f"{updated_dependency.package}")
            cols[1].label(text=f"{_version}")
            cols[2].label(text=f"{_path}")
            cols[3].label(text=f"{True}")


def redraw_preferences():
    try:
        unregister_class(BLENDARMOCAP_preferences)
    except RuntimeError:
        pass

    register_class(BLENDARMOCAP_preferences)
