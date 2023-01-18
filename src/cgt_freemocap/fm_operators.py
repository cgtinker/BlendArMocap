import bpy
import logging
import addon_utils
from pathlib import Path
from . import fm_utils, fm_session_loader


class OT_Freemocap_Quickload_Operator(bpy.types.Operator):
    bl_label = "Load Freemocap Session"
    bl_idname = "wm.cgt_quickload_freemocap_operator"
    bl_description = "Load Freemocap Session data from directory."

    user = freemocap_session_path = _timer = session_loader = None

    def execute(self, context):
        """ Loads Freemocap data from session directory. """
        self.user = context.scene.cgtinker_freemocap

        # check if modal is already running
        if self.user.modal_active:
            self.user.modal_active = False
            return {'CANCELLED'}

        # validate session directory
        if not fm_utils.is_valid_session_directory(self.user.freemocap_session_path):
            self.user.modal_active = False
            self.report({'ERROR'}, f"Session directory not valid. {self.user.freemocap_session_path}")
            return {'FINISHED'}

        # load data
        self.user.modal_active = True
        if self.user.load_raw and self.user.quickload:
            loader = fm_session_loader.FreemocapLoader(
                self.user.freemocap_session_path, modal_operation=False, raw=True
            )
            loader.quickload_raw()

        elif self.user.quickload:
            loader = fm_session_loader.FreemocapLoader(
                self.user.freemocap_session_path, modal_operation=False, raw=False
            )
            loader.quickload_processed()

        self.user.modal_active = False
        self.report({'INFO'}, "Finished importing")
        return {'FINISHED'}


class WM_Load_Freemocap_Operator(bpy.types.Operator):
    bl_label = "Load Freemocap Session"
    bl_idname = "wm.cgt_load_freemocap_operator"
    bl_description = "Load Freemocap Session data from directory."

    user = freemocap_session_path = _timer = session_loader = None

    def execute(self, context):
        """ Loads Freemocap data from session directory. """
        self.user = context.scene.cgtinker_freemocap

        # check if modal is already running
        if self.user.modal_active:
            self.user.modal_active = False
            return {'CANCELLED'}

        # validate session directory
        if not fm_utils.is_valid_session_directory(self.user.freemocap_session_path):
            self.user.modal_active = False
            self.report({'ERROR'}, f"Session directory not valid. {self.user.freemocap_session_path}")
            return {'FINISHED'}

        # init loader
        self.session_loader = fm_session_loader.FreemocapLoader(
            self.user.freemocap_session_path, modal_operation=True)
        self.user.modal_active = True

        # init modal
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, f'Start running modal operator {self.__class__.__name__}')
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            if self.user.modal_active:
                self.session_loader.update()
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)
        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear time and remove manager. """
        self.user.modal_active = False
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        logging.debug("FINISHED DETECTION")
        return {'FINISHED'}


class WM_FMC_bind_freemocap_data_to_skeleton(bpy.types.Operator):
    bl_label = "Bind `freemocap` to skeleton    "
    bl_idname = "wm.fmc_bind_freemocap_data_to_skeleton"
    bl_description = "Bind freemocap animation data to a rigify skeleton (rig)"

    def execute(self, context):
        # set generated rigify rig
        # TODO: rigify generate doesnt get called
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.pose.rigify_generate()
        bpy.context.object.data.layers[31] = True

        # set transfer props
        cgtinker_transfer = context.scene.cgtinker_transfer  # noqa
        cgtinker_transfer.selected_rig = bpy.context.active_object
        cgtinker_transfer.selected_driver_collection = bpy.data.collections.get('cgt_DRIVERS')
        cgtinker_transfer.transfer_types = 'Rigify_Humanoid_DefaultFace_v0.6.1'

        bpy.ops.button.cgt_object_apply_properties()
        return {'FINISHED'}


class WM_FMC_load_synchronized_videos(bpy.types.Operator):
    bl_label = "load synchronized freemocap videos"
    bl_idname = "wm.fmc_load_synchronized_videos"
    bl_description = "Load synchronized freemocap videos using 'Images as Planes' addon"

    user = None

    def execute(self, context):
        self.user = context.scene.cgtinker_freemocap  # noqa
        freemocap_session_path = Path(self.user.freemocap_session_path)

        addon_utils.enable("io_import_images_as_planes")
        if not fm_utils.is_valid_session_directory(str(freemocap_session_path)):
            self.report({'ERROR'}, f"Session directory not valid. {self.user.freemocap_session_path}")
            return {'CANCELLED'}

        try:
            logging.debug('loading videos as planes...')
            vidFolderPath = freemocap_session_path / 'SyncedVideos'

            # %% create world origin
            bpy.ops.object.empty_add(type='ARROWS')
            world_origin_axes = bpy.context.active_object
            world_origin_axes.name = 'world_origin'  # will stay at origin

            world_origin = bpy.data.objects['world_origin']

            number_of_videos = len(list(vidFolderPath.glob('*.mp4')))

            vid_location_scale = 4

            for vid_number, thisVidPath, in enumerate(vidFolderPath.glob('*.mp4')):
                logging.debug(thisVidPath)
                # use 'images as planes' add on to load in the video files as planes
                bpy.ops.import_image.to_plane(files=[{"name": thisVidPath.name}], directory=str(thisVidPath.parent),
                                              shader='EMISSION', )
                this_vid_as_plane = bpy.context.active_object
                this_vid_as_plane.name = 'vid_' + str(vid_number)

                vid_x = (vid_number - number_of_videos / 2) * vid_location_scale

                this_vid_as_plane.location = [vid_x, vid_location_scale, vid_location_scale]
                this_vid_as_plane.rotation_euler = [3.14152 / 2, 0, 0]
                this_vid_as_plane.scale = [vid_location_scale * 1.5] * 3
                this_vid_as_plane.parent = world_origin

                # create a light
                # bpy.ops.object.light_add(type='POINT', radius=1, align='WORLD')
        except Exception as e:
            self.report({'ERROR'}, f'Failed to load videos to Blender scene. {e}')
            return {'CANCELLED'}
        self.report({'INFO'}, f"Imported session videos as planes.")
        return {'FINISHED'}


classes = [
    OT_Freemocap_Quickload_Operator,
    WM_FMC_load_synchronized_videos,
    WM_FMC_bind_freemocap_data_to_skeleton,
    WM_Load_Freemocap_Operator
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    try:
        unregister()
    except RuntimeError:
        pass

    register()
