from _blender.rig.utils import pose_driver_expressions
from _blender.utils import objects
from utils import m_V
import importlib

importlib.reload(m_V)
importlib.reload(pose_driver_expressions)
importlib.reload(objects)


class LimbDriver:
    driver_target: str
    rigify_joint: list

    driver_origin: pose_driver_expressions.PoseDriver
    joint_head: pose_driver_expressions.PoseDriver
    joint_tail: pose_driver_expressions.PoseDriver
    pose_drivers: list

    rigify_joint_length: float = .0
    offset: list = [0, 0, 0]

    def __init__(self, driver_target, driver_origin, detected_joint, rigify_joint, pose_bones, offset_bone=None):
        # actual drivers
        self.driver_target = driver_target
        self.driver_origin = pose_driver_expressions.PoseDriver(driver_origin)
        # detected results
        self.joint_head = pose_driver_expressions.PoseDriver(detected_joint[0])
        self.joint_tail = pose_driver_expressions.PoseDriver(detected_joint[1])
        # referencing pose drivers
        self.pose_drivers = [self.driver_origin, self.joint_head, self.joint_tail]
        # rigify joint length
        self.set_rigify_joint_length(rigify_joint, pose_bones)

        if offset_bone is not None:
            self.set_pose_driver_offset(pose_bones, offset_bone, )

    def set_rigify_joint_length(self, rigify_joint, pose_bones):
        """ sets rigify joint length which should be targeted by the drivers """
        self.rigify_joint_length = m_V.get_vector_distance(
            pose_bones[rigify_joint[0]].head,
            pose_bones[rigify_joint[1]].head)

    def set_expressions(self):
        """ sets the expressions for blender internal drivers.
            the driver should copy the motion of the detection results,
            while keeping an offsets to it's parent based on the target rig. """
        self.set_driver_origin()
        self.set_joint_head()
        self.set_joint_tail()

    def set_driver_origin(self):
        """ previously calculated driver as origin """
        expression = self.driver_origin.get_driver_origin_expression(self.driver_target)
        self.driver_origin.expressions = [expression]

    def set_joint_head(self):
        """ detected joint head """
        expression = self.joint_head.get_detected_joint_head_expression(self.driver_target)
        self.joint_head.expressions = [expression]

    def set_joint_tail(self):
        """ detected joint tail yields the main expression """
        self.joint_tail.offset = self.offset
        self.joint_tail.length = self.rigify_joint_length

        scale_expression = self.joint_tail.get_detected_joint_length_expression(self.driver_target)
        main_expression = self.joint_tail.get_driver_main_expression(self.driver_target)
        self.joint_tail.expressions = [scale_expression, main_expression]

    def set_pose_driver_offset(self, pose_bones, bone_name):
        """ offset for individual arm joints """
        # remove constraint
        for constraint in pose_bones[bone_name].constraints:
            if constraint.type == "COPY_LOCATION":
                pose_bones[bone_name].constraints.remove(constraint)

        # calc offset
        bone_pos = pose_bones[bone_name].head
        ob = objects.get_object_by_name(self.joint_tail.name)
        tar = ob.location
        self.offset = bone_pos - tar
