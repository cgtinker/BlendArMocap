import bpy
import addon_utils
from ..cgt_naming import COLLECTIONS
from pathlib import Path


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