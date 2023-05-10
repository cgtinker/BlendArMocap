import logging
import bpy

from queue import Queue
from multiprocessing import Process

from .cgt_core_socket import server_result_processor, tcp_server


class WM_CGT_mediapipe_data_socket_operator(bpy.types.Operator):
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
    WM_CGT_mediapipe_data_socket_operator
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
