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

import logging
import bpy
from pathlib import Path
from ..utils import objects
from ...cgt_naming import COLLECTIONS
from ...cgt_ipc import tcp_server, server_result_processor
from multiprocessing import Queue, Process


# region TRANSFER
class OT_UI_CGT_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to cgt_rig"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        from ..cgt_rig import rigify_pose, rigify_face, rigify_fingers

        col_mapping = {
            COLLECTIONS.hands: rigify_fingers.RigifyHands,
            COLLECTIONS.face:  rigify_face.RigifyFace,
            COLLECTIONS.pose:  rigify_pose.RigifyPose
        }

        user = bpy.context.scene.m_cgtinker_mediapipe

        selected_driver_collection = user.selected_driver_collection.name
        selected_armature = user.selected_rig.name_full

        print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

        driver_collections = objects.get_child_collections(selected_driver_collection)
        for col in driver_collections:
            armature = objects.get_armature(selected_armature)
            driver_objects = objects.get_objects_from_collection(col)
            col_mapping[col](armature, driver_objects)

        # input_manager.transfer_animation()
        return {'FINISHED'}


class OT_UI_CGT_smooth_empties_in_col(bpy.types.Operator):
    bl_label = "Smooth"
    bl_idname = "button.smooth_empties_in_col"
    bl_description = "Smooth the animation data in the selected collection."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        # safe current area, switching to graph editor area
        current_area = bpy.context.area.type
        layer = bpy.context.view_layer

        # get objs from selected cols
        user = bpy.context.scene.m_cgtinker_mediapipe
        selected_driver_collection = user.selected_driver_collection.name
        driver_collections = objects.get_child_collections(selected_driver_collection)
        objs = []
        for col in driver_collections:
            objs += objects.get_objects_from_collection(col)

        print("selecting objects")
        for ob in objs:
            ob.select_set(True)
        layer.update()

        print("start smoothing process")
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.euler_filter()
        bpy.ops.graph.sample()
        bpy.ops.graph.smooth()

        print("process finished")
        bpy.context.area.type = current_area
        for ob in objs:
            ob.select_set(False)
        layer.update()
        layer.update()

        return {'FINISHED'}


class OT_CGT_Gamerig(bpy.types.Operator):
    bl_label = "Rigify to Gamerig"
    bl_idname = "button.cgt_generate_gamerig"
    bl_description = "Transfer the animation from a generated rigify rig to a metarig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = bpy.context.scene.m_cgtinker_mediapipe
        metarig = user.selected_metarig
        rig = user.selected_rig

        d = {}
        if metarig is None:
            logging.warning("No rig to transfer to selected.")
            return {'CANCELED'}

        if rig is None:
            logging.warning("No rig to transfer from selected.")
            return {'CANCELED'}

        for bone in metarig.data.bones:
            d[bone.name] = ''

        rig = bpy.data.objects['rig']
        for bone in rig.data.bones:
            if bone.layers[29] or bone.use_deform:
                name = bone.name
                if name.startswith('DEF-'):
                    name = name.replace('DEF-', '')
                if name not in d:
                    d[name] = None
                else:
                    d[name] = bone.name

        for key, value in d.items():
            if value != None:
                constraint = metarig.pose.bones[key].constraints.new('COPY_TRANSFORMS')
                constraint.target = rig
                constraint.subtarget = value
                constraint.influence = 1

        return {'FINISHED'}


class OT_CGT_RegenerateMetarig(bpy.types.Operator):
    """ TODO: Implement regen """
    bl_label = "Regenerate Metarig"
    bl_idname = "button.cgt_regenerate_metarig"
    bl_description = "Regenerates the metarig from a rigify rig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context: bpy.context):
        user = bpy.context.scene.m_cgtinker_mediapipe
        if not user.selected_rig:
            logging.error("Ensure to select a generated rig to regenerate it's metarig.")
            return {'CANCELED'}

        bone_data = {}
        source_rig = user.selected_rig.name

        # generate new metarig
        bpy.ops.object.armature_human_metarig_add()
        dest_rig = bpy.context.object.name

        def edit_rig(rigname):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[rigname].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[rigname]
            bpy.ops.object.mode_set(mode='EDIT')

        # select source rig and copy values
        edit_rig(source_rig)
        for b in bpy.data.objects[source_rig].data.edit_bones:
            bone_data[b.name] = (b.head.copy(), b.tail.copy(), b.roll)

        # apply values to dest rig
        edit_rig(dest_rig)
        for b in bpy.data.objects[dest_rig].data.edit_bones:
            b.head, b.tail, b.roll = bone_data[b.name]

        bpy.ops.object.mode_set(mode='OBJECT')


class OT_UI_CGT_toggle_drivers_button(bpy.types.Operator):
    bl_label = "Toggle Drivers"
    bl_idname = "button.cgt_toggle_drivers_button"
    bl_description = "Toggle drivers to improve performance while motion capturing"
    # TODO: IMPLEMENT PROPER WAY TO TOGGLE

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        user = bpy.context.scene.m_cgtinker_mediapipe  # noqa
        user.toggle_drivers_bool = not user.toggle_drivers_bool
        print("toggled", user.toggle_drivers_bool)

        driver_collections = objects.get_child_collections('CGT_DRIVERS')
        objs = objects.get_objects_from_collection('CGT_DRIVERS')
        print(objs)
        return {'FINISHED'}
# endregion

class WM_CGT_modal_detection_operator(bpy.types.Operator):
    bl_label = "Feature Detection Operator"
    bl_idname = "wm.cgt_feature_detection_operator"
    bl_description = "Detect solution in Stream."

    _timer = None
    detection_handler = None
    user = None

    def execute(self, context):
        """ Runs movie or stream detection depending on user input. """
        self.user = context.scene.m_cgtinker_mediapipe  # noqa

        # hacky way to check if operator is running
        if self.user.modal_active is True:
            self.user.modal_active = False
            return {'FINISHED'}
        else:
            self.user.modal_active = True

        # create a detection handler
        from ...mediapipe_processing_manager import RealtimeDataProcessingManager
        detection_type = self.user.enum_detection_type
        self.detection_handler = RealtimeDataProcessingManager(detection_type, "BPY")

        # initialize detector using user inputs
        frame_start = bpy.context.scene.frame_start
        print(self.user.detection_input_type)
        if self.user.detection_input_type == 'movie':
            mov_path = bpy.path.abspath(self.user.mov_data_path)
            print("Path to mov:", mov_path)
            if not Path(mov_path).is_file():
                print("GIVEN PATH IS NOT VALID")
                self.user.modal_active = False
                return {'FINISHED'}
            self.detection_handler.init_detector(str(mov_path), "sd", 0, frame_start, 1, 1)

        elif self.user.detection_input_type == 'freemocap':
            self.detection_handler = RealtimeDataProcessingManager("FREEMOCAP", "BPY")
            freemocap_session_path = Path(bpy.path.abspath(self.user.freemocap_session_path)).parent
            print("Path to freemocap_session_path:", freemocap_session_path)
            if not Path(freemocap_session_path).is_dir():
                print("GIVEN PATH IS NOT VALID")
                self.user.modal_active = False
                return {'FINISHED'}
            self.detection_handler.init_detector(input_type=2)  # input_type=2 <- freemocap_session

        else:
            camera_index = self.user.webcam_input_device
            dimensions = self.user.enum_stream_dim
            backend = int(self.user.enum_stream_type)
            key_step = self.user.key_frame_step
            self.detection_handler.init_detector(camera_index, dimensions, backend, frame_start, key_step, 0)

        # initialize the bridge from the detector to blender
        self.detection_handler.init_bridge()

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        print(f"RUNNING {detection_type} DETECTION AS MODAL")
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Run detection as modal operation, finish with 'Q', 'ESC' or 'RIGHT MOUSE'. """
        if event.type == "TIMER":
            running = self.detection_handler.realtime_data_provider.frame_detection_data()
            if running:
                return {'PASS_THROUGH'}
            else:
                return self.cancel(context)

        if event.type in {'Q', 'ESC', 'RIGHT_MOUSE'} or self.user.modal_active is False:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing detection clear the handlers. """
        bpy.context.scene.m_cgtinker_mediapipe.modal_active = False # noqa
        del self.detection_handler
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("FINISHED DETECTION")
        return {'FINISHED'}


class WM_CGT_modal_connection_listener_operator(bpy.types.Operator):
    bl_label = "Local Connection Listener"
    bl_idname = "wm.cgt_local_connection_listener"
    bl_description = "Receives BlendArMocaps Mediapipe Data from Local Host."

    queue: Queue
    processor: server_result_processor.ServerResultsProcessor
    process: Process
    timer: None
    server = None

    def execute(self, context):
        """ Initialize connection to local host and start modal. """
        if context.scene.m_cgtinker_mediapipe.connection_operator_running:
            print("SERVER STILL ACTIVE")
            return {'CANCELLED'}

        # queue to stage received results
        self.queue = Queue()
        self.processor = server_result_processor.ServerResultsProcessor()

        # start server
        self.server = tcp_server.Server(self.queue)
        self.server.exec()

        # start server handle as seperate process
        self.process = Process(target=self.server.handle, args=())
        self.process.daemon = True
        self.process.start()

        # add a timer property and start running
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        context.scene.m_cgtinker_mediapipe.connection_operator_running = True
        print(f"RUNNING CONNECTION AS MODAL OPERATION")
        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        """ Server runs on separate thread and pushes results in queue,
            The results are getting processed and linked to blender. """
        if event.type == "TIMER":
            # putting message in cgt_icp/chunk_parser
            payload = self.queue.get()
            if payload:
                if payload == "DONE":
                    return self.cancel(context)
                # payload contains capture results and the corresponding frame
                self.processor.exec(payload)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        """ Upon finishing connection. """
        self.process.join()  # await finish

        # additional layer of security, shouldn't be required
        if self.process.is_alive():
            print("PROCESS STILL ALIVE")
            self.process.terminate()
            self.server.shutdown()
            print("PROCESS TERMINATED, SERVER SHUTDOWN")

        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("STOPPED CONNECTION")

        context.scene.m_cgtinker_mediapipe.connection_operator_running = False
        return {'FINISHED'}


classes = [
    OT_UI_CGT_transfer_anim_button,
    OT_UI_CGT_smooth_empties_in_col,
    OT_CGT_Gamerig,
    # OT_CGT_RegenerateMetarig,
    OT_UI_CGT_toggle_drivers_button,
    WM_CGT_modal_detection_operator,
    WM_CGT_modal_connection_listener_operator
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
