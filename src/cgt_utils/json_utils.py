import json
# from src.cgt_naming import POSE
#
# pose_constraints = {
#         # plain copy rotation
#         POSE.hip_center:       ["torso", "COPY_ROTATION"],
#         POSE.shoulder_center:  ["chest", "COPY_ROTATION"],
#
#         # copy pose driver location
#         POSE.left_hand_ik:     ["hand_ik.R", "COPY_LOCATION_WORLD"],
#         POSE.right_hand_ik:    ["hand_ik.L", "COPY_LOCATION_WORLD"],
#         POSE.left_forearm_ik:  ["forearm_tweak.R", "COPY_LOCATION_WORLD"],
#         POSE.right_forearm_ik: ["forearm_tweak.L", "COPY_LOCATION_WORLD"],
#
#         # damped track to pose driver
#         POSE.left_index_ik:    ["hand_ik.R", "LOCKED_TRACK"],
#         POSE.right_index_ik:   ["hand_ik.L", "LOCKED_TRACK"],
#
#         # leg poses
#         POSE.left_shin_ik:     ["shin_tweak.R", "COPY_LOCATION_WORLD"],
#         POSE.right_shin_ik:    ["shin_tweak.L", "COPY_LOCATION_WORLD"],
#         POSE.left_foot_ik:     ["foot_ik.R", "COPY_LOCATION_WORLD"],
#         POSE.right_foot_ik:    ["foot_ik.L", "COPY_LOCATION_WORLD"]
#     }
#
#
# source = pose_constraints
# res = json.dumps(source, indent=4)
#
# print(source)
# print(res)