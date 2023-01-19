import bpy
from typing import List
from collections import namedtuple


class FCurveHelper:
    def __init__(self):
        """ Helper class to easily set and insert data to an objects f-curves. """
        self.location, self.scale, self.rotation_euler = [None, None, None], [None, None, None], [None, None, None]
        self.rotation_quaternion = [None]*4

    def get_f_curves(self, data_path) -> List[bpy.types.FCurve]:
        if not hasattr(self, data_path):
            raise KeyError
        return getattr(self, data_path, [])

    def insert(self, data_path: str, frame: int, *args: float):
        """ data_path: String Enum [location, scale, rotation_euler, rotation_quaternion] """
        f_curves = self.get_f_curves(data_path)
        for fc, sample in zip(f_curves, args):
            fc.keyframe_points.insert(
                frame=frame, value=sample, options={'FAST'}, keyframe_type='JITTER')

    def foreach_set(self, data_path: str, frames: List[int], *args: List[float]):
        """ Set multiple keyframes at once.
            data_path: String Enum [location, scale, rotation_euler, rotation_quaternion]
            frames: flat list of int
            args: flat lists of float """
        f_curves = self.get_f_curves(data_path)

        for samples, fc in zip(args, f_curves):
            if hasattr(fc.keyframe_points, 'clear'):
                fc.keyframe_points.clear()
            fc.keyframe_points.add(count=len(frames))
            fc.keyframe_points.foreach_set("co", [x for co in zip(frames, samples) for x in co])
            fc.update()

    def update(self, data_path: str):
        if not hasattr(self, data_path):
            raise KeyError

        for fc in getattr(self, data_path, []):
            fc.update()

    def __str__(self):
        s = f'locations: {self.location}\n'
        s += f'scale: {self.scale}\n'
        s += f'rotation_euler: {self.rotation_euler}\n'
        s += f'rotation_quaternion: {self.rotation_quaternion}\n'
        return s


def create_actions(objects, overwrite: bool = True):
    actions = []

    # get or create actions for objs
    for ob in objects:
        action_name = ob.name
        ad = ob.animation_data_create()

        # remove old action from objects animation data (default)
        action_data = bpy.data.actions
        if action_name in action_data:
            if overwrite is True:
                action_data.remove(action_data[action_name])
            else:
                actions.append(action_data[action_name])
                ad.action = action_data[action_name]
                continue

        # create new action
        new_action = bpy.data.actions.new(action_name)
        actions.append(new_action)
        ad.action = new_action

    fc_helpers = []

    # get or create fcurves for actions
    for action in actions:
        # add existing data_paths to helper obj
        helper = FCurveHelper()
        offset, last = 0, None

        fc_data_paths = set()
        for i, fc in action.fcurves.items():
            if fc.group.name != last:
                fc_data_paths.add(fc.group.name)
                last = fc.group.name
                offset = i
            m_data_path = getattr(helper, fc.group.name)
            m_data_path[i - offset] = fc

        # add new fcurve
        for data_path, indexes in [('location', 3), ('rotation_euler', 3), ('scale', 3), ('rotation_quaternion', 4)]:
            if data_path in fc_data_paths:
                continue

            for i in range(0, indexes):
                try:
                    fc = action.fcurves.new(
                        data_path=data_path,
                        index=i,
                        action_group=data_path)

                    m_data_path = getattr(helper, fc.group.name)
                    m_data_path[i] = fc
                except RuntimeError:
                    pass

        fc_helpers.append(helper)
    return fc_helpers


def main():
    helpers = create_actions(bpy.data.objects)
    helpers[0].insert('location', 1, *[3, 2, 1])
    helpers[0].insert('location', 13, *[1, 2, 4])
    helpers[0].insert('location', 21, *[10, 3, 0])
    helpers[0].insert('location', 32, *[4, 1, 1])
    helpers[0].update('location')
