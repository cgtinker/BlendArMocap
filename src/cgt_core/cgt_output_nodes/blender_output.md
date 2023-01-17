# Blender output for mediapipe data


Sets up objects, once created gets instances.
The process is based on object names, changing object names may lead to issues.

Insert keyframes to objects on update based on `cgt_calculator_nodes` output.
Overwrites previously set keyframes if available.

Might gets slow if many keyframes have been set within blender as blender updates object fcurves on each insert.
Consider to use `cgt_bpy.cgt_fc_actions` to directly set keyframes to objects when realtime updates are not required.