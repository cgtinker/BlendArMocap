from __future__ import annotations
from typing import List

import bpy
import numpy as np

from src.cgt_core.cgt_naming import HAND, POSE
from src.cgt_core.cgt_bpy import objects
from src.cgt_core.cgt_utils import cgt_math

pose_hierarchy = {
    POSE.hip_center: {
        POSE.shoulder_center: {
            POSE.nose:           {
                POSE.mouth_left:      {'#': {'#'}},
                POSE.mouth_right:     {'#': {'#'}},
                POSE.left_eye_inner:  {
                    POSE.left_eye: {
                        POSE.left_eye_outer: {
                            POSE.left_ear: {
                                '#': {'#'}
                            }
                        }
                    }
                },
                POSE.right_eye_inner: {
                    POSE.right_eye: {
                        POSE.right_eye_outer: {
                            POSE.right_ear: {
                                '#': {'#'}
                            }
                        }
                    }
                }
            },
            POSE.left_shoulder:  {
                POSE.left_elbow: {
                    POSE.left_wrist: {
                        POSE.left_pinky: {'#': {'#'}},
                        POSE.left_index: {'#': {'#'}},
                        POSE.left_thumb: {'#': {'#'}},
                    }
                }
            },
            POSE.right_shoulder: {
                POSE.right_elbow: {
                    POSE.right_wrist: {
                        POSE.right_pinky: {'#': {'#'}},
                        POSE.right_index: {'#': {'#'}},
                        POSE.right_thumb: {'#': {'#'}},
                    }
                }
            }
        },
        POSE.left_hip:        {
            POSE.left_knee: {
                POSE.left_ankle: {
                    POSE.left_heel: {
                        POSE.left_foot_index: {'#': {'#'}}
                    }
                }
            }
        },
        POSE.right_hip:       {
            POSE.right_knee: {
                POSE.right_ankle: {
                    POSE.right_heel: {
                        POSE.right_foot_index: {'#': {'#'}}
                    }
                }
            }
        },
    }
}

hand_hierarchy = {
    HAND.wrist: {
        HAND.thumb_cmc:         {
            HAND.thumb_mcp: {
                HAND.thumb_ip: {
                    HAND.thumb_tip: {
                        '#': '#'}}}},
        HAND.index_finger_mcp:  {
            HAND.index_finger_pip: {
                HAND.index_finger_dip: {
                    HAND.index_finger_tip: {
                        '#': '#'}}}},
        HAND.middle_finger_mcp: {
            HAND.middle_finger_pip: {
                HAND.middle_finger_dip: {
                    HAND.middle_finger_tip: {
                        '#': '#'}}}},
        HAND.ring_finger_mcp:   {
            HAND.ring_finger_pip: {
                HAND.ring_finger_dip: {
                    HAND.ring_finger_tip: {
                        '#': '#'}}}},
        HAND.pinky_mcp:         {
            HAND.pinky_pip: {
                HAND.pinky_dip: {
                    HAND.pinky_tip: {
                        '#': '#'}}}},
    }
}


class Trie:
    def __init__(self, trie=None):
        self.trie = {}
        if trie is not None:
            self.trie = trie

    def __iter__(self, *args):
        def recv(branch):
            for node in branch:
                yield node
                if node == '#':
                    continue
                yield from recv(branch[node])

        for node in self.trie:
            yield node
            yield from recv(self.trie[node])

    def __len__(self):
        return len([0 for _ in self if _ != '#'])

    def get_depth(self):
        max_depth = 0

        def recv(branch, depth):
            nonlocal max_depth
            if depth > max_depth:
                max_depth = depth
            depth += 1
            for node in branch:
                if node == '#':
                    continue
                recv(branch[node], depth)

        for node in self.trie:
            recv(self.trie[node], 0)

        return max_depth

    def __getitem__(self, key):
        return self.trie[key]

    def __str__(self):
        def recv(name, branch, depth):
            if name == '#':
                return

            tabs = "".join(['\t'] * depth)
            bracelet = "{"
            print(f"\n{tabs}{name}: {bracelet}")

            for name in branch:
                recv(name, branch[name], depth + 1)

            tabs = "".join(['\t'] * depth)
            print(tabs, "}")

        for node in self.trie:
            recv(node, self.trie[node], 0)

        return ''


class ObjectTrie(Trie):
    def from_children(self, parents: List[bpy.types.Object]) -> ObjectTrie:
        """ Creates a trie based on child objects from the input object.
            Leafs contain a '#'. """

        def add_childs2branch(obj, branch: dict):
            if not obj.children:
                branch['#'] = '#'

            for ob in obj.children:
                branch[ob] = {}
                add_childs2branch(ob, branch[ob])

        self.trie = {}
        for par in parents:
            self.trie[par] = {}
            branch = self.trie[par]
            add_childs2branch(par, branch)

        return self

    def global2local(self, target_trie: ObjectTrie, dist_trie: Trie) -> ObjectTrie:
        """ Sets parented trie objects in local space corresponding to target space while keeping static distances. """
        def recv(obj, target, dist, branch, tar_branch, dist_branch, parent=None):
            nonlocal root
            if obj == '#':
                return

            # parent == previous target
            if parent is not None:
                # mp result distance between joints is not static
                cur_dist = cgt_math.get_vector_distance(
                    np.array(target.location),
                    np.array(parent.location)
                )

                obj.location = np.array(root.location) + (dist / cur_dist) * np.array(
                    (target.location - parent.location))
                obj.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_current)

            for next_obj, next_target, next_dist in zip(branch, tar_branch, dist_branch):
                recv(next_obj, next_target, next_dist, branch[next_obj], tar_branch[next_target],
                     dist_branch[next_dist], target)

        for node, root, dist in zip(self.trie, target_trie.trie, dist_trie.trie):
            branch = self.trie[node]
            loc_branch = target_trie[root]
            dist_branch = dist_trie[dist]
            recv(node, root, dist, branch, loc_branch, dist_branch)

        return self

    def set_parents(self) -> ObjectTrie:
        """ Parents objects based on the Trie Layout. """

        def recv(obj, branch, parent=None):
            if obj == '#':
                return

            if parent is not None:
                obj.parent = parent

            for name in branch:
                recv(name, branch[name], obj)

        for parent in self.trie:
            branch = self.trie[parent]
            recv(parent, branch)

        return self


class StringTrie(Trie):
    def rename_entries(self, suffix: str = "", prefix: str = "", instance_type: type = str) -> StringTrie:
        """ Renames all entries within a trie matching the instance type. """
        copy_dict = {}

        def recv(name, branch, copy):
            if name == '#':
                copy['#'] = {'#'}
                return

            if isinstance(name, instance_type):
                key = f'{suffix}{name}{prefix}'
            else:
                key = name
            copy[key] = dict()

            for name in branch:
                recv(name, branch[name], copy[key])

        for node in self.trie:
            recv(node, self.trie[node], copy_dict)

        self.trie = copy_dict
        return self

    def to_objects(self) -> ObjectTrie:
        """ Creates object trie from string trie.
            Creates objects if they not exists. """

        copy_dict = {}

        def recv(name, branch, copy):
            if name == '#':
                copy['#'] = {'#'}
                return

            if isinstance(name, str):
                key = objects.get_object_by_name(name)
                if key is None:
                    key = objects.add_empty(0.01, name)
            else:
                raise TypeError(name)

            copy[key] = dict()

            for name in branch:
                recv(name, branch[name], copy[key])

        for node in self.trie:
            recv(node, self.trie[node], copy_dict)

        return ObjectTrie(copy_dict)


def get_parents():
    def is_root(obj: bpy.types.Object) -> bool:
        """ Returns True if object is a parent empty object with children. """
        if obj.parent == None and obj.children:
            return True
        return False

    return [obj for obj in bpy.context.selected_objects if is_root(obj)]


def convert_obj2dist_trie(trie: ObjectTrie) -> Trie:
    """ Returns distances from child to parent as Trie """
    copy_dict = {}

    def recv(ob, branch, copy, parent=None):
        if ob == '#':
            print(ob, parent)
            copy['#'] = {'#'}
            return

        if parent is not None:
            key = cgt_math.get_vector_distance(
                np.array(ob.location),
                np.array(parent.location)
            )
        else:
            key = -1

        while key in copy:
            key += 0.00000000000000001
        copy[key] = dict()

        for next_ob in branch:
            recv(next_ob, branch[next_ob], copy[key], ob)

    for node in trie.trie:
        print(node)
        recv(node, trie[node], copy_dict)

    return Trie(copy_dict)


def object_trie2armature(trie: dict[bpy.types.Object, dict]) -> bpy.types.Object:
    """ Creates an armature based on a parented object trie. """
    name = list(trie.keys())[0].name
    arm = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(arm.name, arm)
    bpy.context.scene.collection.objects.link(rig)

    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.editmode_toggle()

    def global_position(obj):
        m = obj.matrix_world
        return m.to_translation()

    def add_bones_from_branch(target, branch, parent=None):
        nonlocal arm
        if target == '#':
            # remove leafs
            del parent
            return

        cur_bone = arm.edit_bones.new(target.name)
        if parent is None:
            # root of the rig
            cur_bone.head = [0, 0, 0]
            cur_bone.tail = global_position(target)

        else:
            # connected bones
            cur_bone.head = parent.tail
            cur_bone.tail = global_position(target)
            cur_bone.parent = parent
            cur_bone.use_connect = True

        for tar in branch:
            add_bones_from_branch(tar, branch[tar], cur_bone)

    for par in trie:
        branch = trie[par]
        add_bones_from_branch(par, branch)

    bpy.ops.object.editmode_toggle()
    return rig


def add_constraint(bone, target):
    constraint = bone.constraints.new('DAMPED_TRACK')
    constraint.target = target
    constraint.influence = 1
    constraint.track_axis = 'TRACK_Y'


def set_constraints(armature: bpy.types.Object, trie: dict[bpy.types.Object, dict]):
    def recv(obj, branch, parent=None):
        nonlocal armature

        if obj == '#':
            return

        if parent is not None:
            add_constraint(armature.pose.bones[obj.name], obj)
            # obj.parent = parent

        for name in branch:
            recv(name, branch[name], obj)

    for obj in trie:
        branch = trie[obj]
        recv(obj, branch)


def rig_raw_hands():
    def hand_trees(prefix='.L'):
        source_hand = StringTrie(hand_hierarchy).rename_entries(
            suffix="", prefix=prefix, instance_type=str
        ).to_objects()

        parent_hand = StringTrie(hand_hierarchy).rename_entries(
            suffix="GT_", prefix=prefix, instance_type=str
        ).to_objects().set_parents()

        dist_trie = convert_obj2dist_trie(source_hand)
        return (source_hand, parent_hand, dist_trie)

    source_hand_l, parent_hand_l, dist_trie_l = hand_trees('.L')
    source_hand_r, parent_hand_r, dist_trie_r = hand_trees('.R')

    for i in range(0, 100):
        bpy.context.scene.frame_set(i)
        parent_hand_l.global2local(source_hand_l, dist_trie_l)
        parent_hand_r.global2local(source_hand_r, dist_trie_r)

    armature_l = object_trie2armature(parent_hand_l.trie)
    armature_r = object_trie2armature(parent_hand_r.trie)
    set_constraints(armature_l, parent_hand_l.trie)
    set_constraints(armature_r, parent_hand_r.trie)


def rig_raw_pose():
    source = StringTrie(pose_hierarchy).to_objects()
    parent = StringTrie(pose_hierarchy).rename_entries(suffix="GT_", instance_type=str).to_objects().set_parents()
    dist = convert_obj2dist_trie(source)

    for i in range(0, 100):
        bpy.context.scene.frame_set(i)
        parent.global2local(source, dist)

    armature = object_trie2armature(parent.trie)
    set_constraints(armature, parent.trie)


def rigify_gamerig(metarig: bpy.types.Object = None, rig: bpy.types.Object = None) -> None:
    d = {}
    if metarig is None:
        metarig = bpy.data.objects['metarig']

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
        print(key, value)
        if value != None:
            constraint = metarig.pose.bones[key].constraints.new('COPY_TRANSFORMS')
            constraint.target = rig
            constraint.subtarget = value
            constraint.influence = 1


def test():
    trie = StringTrie(hand_hierarchy)

    for node in trie:
        print(node)
    print(trie.get_depth())


def main():
    # rig_raw_hands()
    # rig_raw_pose()
    # rigify_gamerig()
    test()
    pass


if __name__ == '__main__':
    main()

