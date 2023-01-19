from __future__ import annotations
import bpy
import logging
from typing import Optional, Union, List, Dict

from . import tf_get_object_properties, tf_set_object_properties
from ...cgt_core.cgt_bpy import cgt_drivers, cgt_bpy_utils, cgt_collection

from collections import namedtuple

ChainLink = namedtuple('ChainLink', ['obj', 'parent'])
chain_link_items = []


def main(objects: List[bpy.types.Object]):
    """ Apply list of objects containing active cgt_props. """
    global chain_link_items
    chain_link_items.clear()

    logging.debug('########## START TRANSFER ##########')
    for obj in objects:
        manage_object_transfer(obj)
    logging.debug('########## REMAP TRANSFER MANAGED ##########')
    chain_links = find_chain_links(chain_link_items)
    logging.debug('########## FOUND CHAIN LINKS ##########')
    link_object_chain(chain_links)
    logging.debug('########## LINKED CHAINS ##########')


def manage_object_transfer(obj: bpy.types.Object):
    """ Stores chain links in global list and applies drivers which are based on single objects. """
    properties = tf_get_object_properties.get_properties_from_object(obj)
    target_obj, sub_target, target_type = tf_get_object_properties.get_target(properties.target)

    if target_type == 'ABORT':
        return

    if properties.driver_type == 'NONE':
        return

    elif properties.driver_type == 'REMAP':
        remap_object_properties(obj, target_obj, sub_target, target_type, properties)

    elif properties.driver_type == 'CHAIN':
        chain_link_items.append(ChainLink(obj, properties.to_obj))

    elif properties.driver_type == 'REMAP_DIST':
        remap_by_object_distance(obj, target_obj, sub_target, target_type, properties)


def remap_by_object_distance(obj, target_obj, sub_target, target_type, properties):
    # get mapping properties
    dist = tf_get_object_properties.get_distance(properties)
    if dist is None:
        dist = 1

    props = tf_get_object_properties.get_value_by_distance_properties(properties)
    remapping_props = tf_get_object_properties.get_remapping_properties(properties)

    # create driver object
    driver_target = get_driver_target(obj)
    factory = cgt_drivers.DriverFactory(driver_target)

    # apply drivers
    tf_set_object_properties.set_distance_remapping_drivers(factory, props, remapping_props, obj, dist)
    factory.execute()

    if target_type in ['OBJECT', 'ARMATURE']:
        apply_constraints(target_obj, obj, driver_target)
    elif target_type in ['BONE', 'POSE_BONE']:
        apply_constraints(sub_target, obj, driver_target)


def remap_object_properties(obj, target_obj, sub_target, target_type, properties):
    """ Default remap properties (from(min/max), to(min/max), factor...) """
    # get props
    dist = tf_get_object_properties.get_distance(properties)
    if dist is None:
        dist = 1
    remapping_properties = tf_get_object_properties.get_remapping_properties(properties)

    # create driver object
    driver_target = get_driver_target(obj)
    factory = cgt_drivers.DriverFactory(driver_target)

    # apply drivers
    tf_set_object_properties.set_object_remapping_drivers(factory, obj, remapping_properties, dist)
    factory.execute()

    # apply constraints
    if target_type in ['OBJECT', 'ARMATURE']:
        apply_constraints(target_obj, obj, driver_target)
    elif target_type in ['BONE', 'POSE_BONE']:
        apply_constraints(sub_target, obj, driver_target)


def find_chain_links(chain_items: List[ChainLink]) -> Dict[bpy.types.Object, dict]:
    """ Reconstruct chain links in trie structure. """
    def dfs_reconstruct_chain(items: list, branch: dict, target: Optional[bpy.types.Object], seen: set):
        for item in items:
            if item in seen:
                continue

            if item.parent == target:
                seen.add(item)
                branch[item.obj] = {}
                dfs_reconstruct_chain(items, branch[item.obj], item.obj, seen)

    # reconstruct chains in trie structure
    chains_dict = {}
    dfs_reconstruct_chain(chain_items, chains_dict, None, set())
    return chains_dict


def link_object_chain(chains_dict: Dict[bpy.types.Object, dict]):
    """ Apply chain links recursively based on obj trie structure with cgt_props. """
    def apply_chain_link(chain_link_dict, previous_obj, previous_driver):
        for current_obj in chain_link_dict.keys():
            # get properties for chain link
            properties = tf_get_object_properties.get_properties_from_object(current_obj)
            target_obj, sub_target, target_type = tf_get_object_properties.get_target(properties.target)
            tar_dist = tf_get_object_properties.get_distance(properties)
            if not tar_dist:
                tar_dist = 1

            # apply driver
            driver_target = get_driver_target(current_obj)
            factory = cgt_drivers.DriverFactory(driver_target)
            tf_set_object_properties.set_chain_driver(previous_obj, current_obj, previous_driver, factory, tar_dist)
            tf_set_object_properties.set_copy_rotation_driver(current_obj, factory, 'WORLD_SPACE')

            # apply constraints
            if target_type in ['OBJECT', 'ARMATURE']:
                apply_constraints(target_obj, current_obj, driver_target)
            elif target_type in ['BONE', 'POSE_BONE']:
                apply_constraints(sub_target, current_obj, driver_target)

            # next chain link
            apply_chain_link(chain_link_dict[current_obj], current_obj, driver_target)

    for chain_obj in chains_dict.keys():
        # get props for chain start
        properties = tf_get_object_properties.get_properties_from_object(chain_obj)
        target_obj, sub_target, target_type = tf_get_object_properties.get_target(properties.target)

        # set driver for chain start
        driver_target = get_driver_target(chain_obj)
        factory = cgt_drivers.DriverFactory(driver_target)
        tf_set_object_properties.set_copy_location_driver(sub_target, factory, 'WORLD_SPACE')
        tf_set_object_properties.set_copy_rotation_driver(sub_target, factory, 'WORLD_SPACE')

        # recv chain links
        apply_chain_link(chains_dict[chain_obj], chain_obj, driver_target)


# region helper
def get_driver_target(obj: bpy.types.Object) -> bpy.types.Object:
    """ Returns a driver factory which uses an obj based on the name of the input obj.
        Deletes driver object of the same name if it exists. """
    if obj.name + '.D' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj.name + '.D'])
    driver_target = cgt_bpy_utils.add_empty(0.001, obj.name + '.D', 'SPHERE')
    cgt_collection.add_object_to_collection('cgt_DRIVERS', driver_target)
    return driver_target


def apply_constraints(target_obj: Union[bpy.types.Object, bpy.types.PoseBone], obj: bpy.types.Object,
                      driver_target: bpy.types.Object) -> None:
    """ Apply constraint """
    # TODO: move to set_props (?)
    for c in target_obj.constraints:
        if c.active and c.is_valid:
            continue
        target_obj.constraints.remove(c)

    for c in obj.constraints:
        constraint_name = c.type
        constraint_props = tf_get_object_properties.get_constraint_props(c)
        constraint = target_obj.constraints.new(constraint_name)
        constraint_props['target'] = driver_target
        tf_set_object_properties.set_constraint_props(constraint, constraint_props)
# endregion


if __name__ == '__main__':
    main(bpy.context.selected_objects)
