from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional, Callable
import bpy
import numpy as np
from mathutils import Vector, Quaternion, Euler
from src.cgt_core.cgt_bpy import cgt_bpy_utils
from collections import namedtuple


# Targeting following concept:
# - Create a dict trie structure from .json
# - Create objects parented based on trie
# - Create Armature based on objects parenting layout
# - Link Armature bones to objects
# - Animate objects which may keep a static offset to drive rig
# - Create Mesh based on object layout


d = {
    'Cube.001': {
        'Cube.002': {
            'Cube.003': {}
        },
        'Cube.006': {
            'Cube.007': {}
        },
        'Cube.004': {'Cube.005': {'Cube.008': {}}}
    },
}

d2 = {
    "empty_00": {
        "location":       [0, 0, 0],
        "rotation_euler": [25, 0, 10],
        "next":           {
            "empty_01": {
                "location": [1, 0, 1],
                "next":     {}
            },
            "empty_02": {
                "location": [-1, 0, 1],
                "next":     {
                    "empty_03": {
                        "location": [2, 0, 2],
                        "next":     {
                            "empty_04": {
                                "location": [1, 4, 1],
                                "next":     {}
                            }
                        }
                    }
                }
            }
        }
    },
    "empty_05": {
        "location": [0, 0, 0],
        "next":     {
            "empty_06": {
                "location": [1, 0, 1],
                "next":     {}
            }
        }
    }
}


def repr_dict(d: Dict[Any], trie_objects=True) -> str:
    def recv(name, branch, depth):
        tabs = "".join(['\t'] * depth)
        bracelet = "{"
        closing_bracelet = "}"

        # recv trie objects
        if isinstance(branch, TrieObject):
            for key, value in branch.__dict__.items():
                if key == 'next':
                    continue
                print(f"{tabs}{key}: {value}")

            if hasattr(branch, 'next'):
                if not len(branch.next) > 0:
                    print(f"{tabs}{closing_bracelet},\n{tabs}{bracelet}")
                    return

                print(f"{tabs}next:", branch.name, '{')
                recv(branch.name, branch.next, depth + 1)

        # get next dict entries
        elif isinstance(branch, dict):
            if not trie_objects:
                print(f"{tabs}{name}:", '{')

            for name in branch:
                recv(name, branch[name], depth + 1)

        # close dict entry
        tabs = "".join(['\t'] * depth)
        print(f"{tabs}{closing_bracelet},")

    print('{')
    for node in d:
        recv(node, d[node], 1)
    return ''


# region Generators
def gen_flatten(d: Dict[Any]):
    """ Generator to flatten dictonary. """
    for key, value in d.items():
        yield key
        if isinstance(value, dict):
            print('default')
            yield from gen_flatten(value)
        elif hasattr(value, 'next'):
            next = getattr(value, 'next', None)
            if next is not None:
                yield from gen_flatten(next)


def gen_leafs(d: Dict[Any]):
    """ Generator to get dictonary leafs. """
    for key, value in d.items():
        if value == {}:
            yield key
        if isinstance(value, dict):
            yield from gen_leafs(value)


def gen_parents(d: Dict[Any], parent: Any = None):
    """ Generator to get child and parent of dictonary. """
    for child, objects in d.items():
        yield (child, parent)
        if isinstance(objects, dict):
            yield from gen_parents(objects, child)


# endregion


# region Inline
def inline_converter(d: Dict[Any], copy: Dict[Any], method: Callable, parent: Any = None):
    """ Attach a method which gets called during recv call to generate
        other dicts based on the input dict.
        method(copy: Dict[Any], object_name: str, _) -> Dict[Any] """
    for cur, values in d.items():
        branch = method(copy, cur, parent)
        if isinstance(values, dict):
            inline_converter(values, branch, method, cur)


def inline_string2object(copy: Dict[Any], object_name: str, _) -> Dict[Any]:
    """ Get objects using the inline generator. """
    branch = copy[cgt_bpy_utils.add_empty(0.1, object_name)] = {}
    return branch


def inline_calculate_distances(copy: Dict[Any], cur, parent=None):
    """ Calculate distances of objects using the inline generator. """
    if parent is None:
        branch = copy[0] = {}
        return branch

    # calculate distance
    sqrd_dist = np.sum((np.array(cur.location) - np.array(parent.location)) ** 2, axis=0)
    dist = np.sqrt(sqrd_dist)

    # offset distance if key exists in dict
    while dist in copy:
        dist += 0.0000001
    branch = copy[dist] = {}
    return branch


# endregion


# region Converters
def global2local(from_objects: List[bpy.types.Object], to_objects: List[bpy.types.Object],
                 distances: List[float] = None):
    """ Generator for calculating global to local space based on parented object trie. """
    if distances is None:
        distances = [None for _ in range(len(to_objects))]

    for from_parent, tar_obj, tar_dist in zip(from_objects, to_objects, distances):
        cur, parent = from_parent
        if parent is None:
            parent = cur
            yield cur.location
            continue

        if tar_dist is not None:
            # calculate distance from objects, keep static dists
            sqrd_dist = np.sum((np.array(cur.location) - np.array(parent.location)) ** 2, axis=0)
            dist = np.sqrt(sqrd_dist)
            if dist == 0.0:
                dist = 0.0000001
            yield dist / tar_dist * np.array((cur.location - parent.location))

        else:
            yield np.array((cur.location - parent.location))


def objects2armature(trie: dict[bpy.types.Object, dict]) -> bpy.types.Object:
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
        if target == {}:
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

    for node in trie:
        branch = trie[node]
        add_bones_from_branch(node, branch)

    bpy.ops.object.editmode_toggle()
    return rig


def objects2trie(objects: List[bpy.types.Objects]) -> Dict[bpy.types.Object, dict]:
    """ Construct trie structure from object parents. """

    def dfs_construct_trie(objs: list, branch: dict, target: Optional[bpy.types.Object], seen: set):
        for obj in objs:
            if obj in seen:
                continue

            # recv from new branch once the prev obj has been found
            if obj.parent == target:
                seen.add(obj)
                branch[obj] = {}
                dfs_construct_trie(objs, branch[obj], obj, seen)

    trie = {}
    dfs_construct_trie(objects, trie, None, set())
    return trie


# endregion


def set_constraints(armature: bpy.types.Object, trie: dict[bpy.types.Object, dict]):
    def add_constraint(bone, target):
        constraint = bone.constraints.new('DAMPED_TRACK')
        constraint.target = target
        constraint.influence = 1
        constraint.track_axis = 'TRACK_Y'

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


class TrieObject:
    def __init__(self, name):
        self.name = name

        self.location = [0.0, 0.0, 0.0]
        self.rotation_euler = [0.0, 0.0, 0.0]
        self.rotation_quaternion = [1.0, 0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        self.size = 1.0

        # self.dist = None
        self.parent = None
        self.object = None

    def __str__(self):
        s = []
        for k, v in self.__dict__.items():
            if v is None:
                continue

            if isinstance(v, list):
                if v == [0, 0, 0]:
                    continue

            s.append(f"{k}: {v}, ")

        return "".join(s)

    def __repr__(self):
        return self.__str__()


# OPT 1
def armature_from_default_dict():
    objects = {}
    inline_converter(d, objects, inline_string2object)

    distances = {}
    inline_converter(objects, distances, inline_calculate_distances)

    def add_prefix(copy: Dict[Any], name: str, _) -> Dict[Any]:
        branch = copy[name + 'cgt'] = {}
        return branch

    target_names = {}
    inline_converter(d, target_names, add_prefix)

    targets = {}
    inline_converter(target_names, targets, inline_string2object)

    from_objects = list(gen_parents(objects))
    to_objects = list(gen_flatten(targets))
    dists = list(gen_flatten(distances))

    locations = list(global2local(from_objects, to_objects, dists))
    for obj, location in zip(to_objects, locations):
        print(obj, location)
        obj.location = location

    for cur, parent in gen_parents(d):
        if parent is None:
            continue
        c = cgt_bpy_utils.add_empty(0.1, cur + 'cgt')
        p = cgt_bpy_utils.add_empty(0.1, parent + 'cgt')
        c.parent = p

    arm = objects2armature(targets)


# OPT 2
def armature_from_selection():
    objects = bpy.context.selected_objects
    trie = objects2trie(objects)
    repr_dict(trie, False)
    # arm = objects2armature(trie)
    # set_constraints(arm, trie)


# OPT 3
def object_data_from_selection():
    objects = bpy.context.selected_objects
    trie = objects2trie(objects)

    def get_object_data(copy: Dict[Any], obj: TrieObject, parent) -> Dict[Any]:
        object_data = TrieObject(obj.name)

        for key in object_data.__dict__.keys():
            # skips non available keys
            if not hasattr(obj, key):
                continue

            # get values for trie object
            value = getattr(obj, key, None)
            if isinstance(value, (Vector, Euler, Quaternion)):
                value = list(value)
            elif isinstance(value, bpy.types.Object):
                value = value.name

            setattr(object_data, key, value)

        # create branch and switch to next ob
        object_data.next = {}
        copy[obj.name] = object_data
        branch = copy[obj.name].next
        return branch

    object_data = {}
    inline_converter(trie, object_data, get_object_data)

    def repr(d):
        for key, data in d.items():
            print(key)
            if isinstance(data, TrieObject):
                for key, value in data.__dict__.items():
                    if key == 'next':
                        continue
                    print("\t", key, value)
                repr(data.next)

    # repr(object_data)
    for d in gen_flatten_trie_objects(object_data):
        print(d)


def gen_flatten_trie_object_dict(d):
    for key, data in d.items():
        yield (key, None)
        if isinstance(data, TrieObject):
            for key, value in data.__dict__.items():
                if key == 'next':
                    continue
                yield (key, value)
            yield from gen_flatten_trie_object_dict(data.next)


def gen_flatten_trie_objects(d):
    for key, data in d.items():
        if isinstance(data, TrieObject):
            yield data
            yield from gen_flatten_trie_objects(data.next)


# OPT 4
def parse_object_data_dict():
    # init by creating Trie Objects from dict
    def recv(d, copy: dict, current=None, parent=None):
        for key, value in d.items():
            if isinstance(value, dict):
                if key is not 'next':
                    object_name = key
                    new_object = TrieObject(key)
                    branch = copy[new_object] = {}
                    recv(value, branch, new_object)
                else:
                    recv(value, copy, current)
            elif hasattr(current, key):
                setattr(current, key, value)

    trie_data = {}
    recv(d2, trie_data)

    # test getting flat data
    def get_name(copy: Dict[Any], obj: TrieObject, parent) -> Dict[Any]:
        branch = copy[obj.name] = {}
        return branch

    object_names = {}
    inline_converter(trie_data, object_names, get_name)

    # create objects / parents etc (can go nuts here with getter + setter)
    for obj, parent in gen_parents(trie_data):
        obj.object = cgt_bpy_utils.add_empty(0.1, obj.name)
        obj.object.location = obj.location
        if parent is not None:
            obj.parent = cgt_bpy_utils.add_empty(0.1, parent.name)

    # get objects
    def get_objects(copy: Dict[Any], obj: TrieObject, parent) -> Dict[Any]:
        print(obj, parent)
        branch = copy[obj.object] = {}
        return branch

    # create armature
    objects = {}
    inline_converter(trie_data, objects, get_objects)
    print(objects)
    arm = objects2armature(objects)


def main():
    # main___rig_from_dict()
    # rig_from_selection()
    object_data_from_selection()
    # print('done')
    # parse_data_dict()


if __name__ == '__main__':
    print("\n\nnew")
    main()


