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
import logging
import addon_utils
from src.cgt_core.cgt_naming import COLLECTIONS
from pathlib import Path
from . import fm_utils


class WM_Load_Freemocap_Operator(bpy.types.Operator):
    bl_label = "Load Freemocap Session"
    bl_idname = "wm.cgt_load_freemocap_operator"
    bl_description = "Load Freemocap Session data from directory."

    user = freemocap_session_path = _timer = processing_manager = None

    def execute(self, context):
        """ Loads Freemocap data from session directory. """
        self.user = bpy.context.scene.m_cgtinker_mediapipe
        if not self.toggle_modal():
            return {'FINISHED'}

        if not fm_utils.is_valid_session_directory(self.user.freemocap_session_path):
            self.user.modal_active = False
            return {'FINISHED'}

        from src.cgt_core.mediapipe_processing_manager import RealtimeDataProcessingManager
        self.processing_manager = RealtimeDataProcessingManager("FREEMOCAP", "BPY")
        self.processing_manager.init_detector(input_type=2)
        self.processing_manager.init_bridge()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        logging.debug(f'Start running modal operator {self.__class__.__name__}')
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            running = self.processing_manager.realtime_data_provider.get_data()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear time and remove manager. """
        self.user.modal_active = False
        del self.processing_manager
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        logging.debug("FINISHED DETECTION")
        return {'FINISHED'}

    def toggle_modal(self) -> bool:
        """ Check if already a modal is running.
            If, it stops running, else, it starts. """
        # hacky way to check if operator is running
        if self.user.modal_active is True:
            self.user.modal_active = False
            return False
        self.user.modal_active = True
        return True


class WM_FMC_bind_freemocap_data_to_skeleton(bpy.types.Operator):
    bl_label = "Bind `freemocap` to skeleton    "
    bl_idname = "wm.fmc_bind_freemocap_data_to_skeleton"
    bl_description = "Bind freemocap animation data to a rigify skeleton (rig)"

    _timer = None
    detection_handler = None
    user = None

    def execute(self, context):
        print("[green] beep beep lol")
        # load rigify human metarig
        # %% create metarig
        bpy.ops.object.armature_human_metarig_add()
        this_metarig = bpy.context.active_object

        # generate rig
        bpy.ops.pose.rigify_generate()
        this_rig = bpy.context.active_object

        # bind data
        for col in [COLLECTIONS.pose, COLLECTIONS.face, COLLECTIONS.hands]:
            col = bpy.data.collections[col]
            bpy.context.scene.m_cgtinker_mediapipe.selected_driver_collection = col
            bpy.context.scene.m_cgtinker_mediapipe.selected_rig = this_rig
            bpy.ops.button.cgt_transfer_animation_button()  # press button "Transfer Animation"

        bpy.context.object.data.layers[31] = True

        # # copy location - rig & hips_center
        # constraint = this_rig.constraints.new(type="COPY_LOCATION")
        # constraint.target = bpy.data.objects['cgt_hip_center']

        # # hands - disable copy rotations on IK rig
        # bpy.context.object.pose.bones["hand_ik.R"].constraints["Copy Rotation"].enabled = False
        # bpy.context.object.pose.bones["hand_ik.L"].constraints["Copy Rotation"].enabled = False

        return {'FINISHED'}


class WM_FMC_load_synchronized_videos(bpy.types.Operator):
    bl_label = "load synchronized freemocap videos"
    bl_idname = "wm.fmc_load_synchronized_videos"
    bl_description = "Load synchronized freemocap videos using 'Images as Planes' addon"

    user = None

    def execute(self, context):
        print("[cyan] boop boop lol")
        self.user = context.scene.m_cgtinker_mediapipe  # noqa
        freemocap_session_path = Path(self.user.freemocap_session_path)

        addon_utils.enable("io_import_images_as_planes")

        try:
            print('loading videos as planes...')
            vidFolderPath = freemocap_session_path / 'SyncedVideos'
            # %% create world origin

            bpy.ops.object.empty_add(type='ARROWS')
            world_origin_axes = bpy.context.active_object
            world_origin_axes.name = 'world_origin'  # will stay at origin

            world_origin = bpy.data.objects['world_origin']

            number_of_videos = len(list(vidFolderPath.glob('*.mp4')))

            vid_location_scale = 4

            for vid_number, thisVidPath, in enumerate(vidFolderPath.glob('*.mp4')):
                print(thisVidPath)
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
            print('Failed to load videos to Blender scene')
            print(e)

        return {'FINISHED'}