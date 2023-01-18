from __future__ import annotations
from typing import Optional, List
import bpy
import logging


def set_viewport_visibility(collection_name: str, active: bool) -> None:
    """ Sets the visibility of a collection. """
    if collection_exists(collection_name):
        collection = bpy.data.collections.get(collection_name)
        collection.hide_viewport = active


def collection_exists(collection_name: str) -> bool:
    """ Returns if the collection exists. """
    if bpy.data.collections.get(collection_name) is not None:
        return True
    return False


def get_collection(collection_name: str) -> bpy.types.Collection:
    return bpy.data.get(collection_name)


def create_collection(collection_name: str, parent_collection: Optional[str], link: bool = True) -> bool:
    """ Creates a collection which may is child of a parent. """
    if collection_exists(collection_name):
        return False

    collection = bpy.data.collections.new(collection_name)
    if link and parent_collection is None:
        bpy.context.scene.collection.children.link(collection)
    else:
        create_collection(parent_collection, None, True)
        parent = bpy.data.collections.get(parent_collection)
        parent.children.link(collection)
    return True


def remove_collection(collection_name: str, remove_objects: bool = True) -> None:
    """ Removes a collection and the objects it contains. """
    if not collection_exists(collection_name):
        return

    collection = bpy.data.collections.get(collection_name)
    obs = []
    if remove_objects:
        obs = [o for o in collection.cgt_bpy_utils if o.users == 1]
    while len(obs) > 0:
        bpy.data.objects.remove(obs.pop())

    bpy.data.collections.remove(collection)


def add_list_to_collection(
        collection_name: str, objects: List[bpy.types.Object],
        parent_collection: Optional[str] = None, link: bool = True) -> None:
    """ Adds a list of objects to a collection.
        Creates a new collection if it doesn't exist. """
    if not collection_exists(collection_name):
        create_collection(collection_name, parent_collection, link)

    for obj in objects:
        _obj_to_collection(collection_name, obj)


def add_object_to_collection(
        collection_name: str, obj: bpy.types.Object,
        parent_collection=None, link=True) -> bool:
    """ Adds an Object to a collection, creates a new collection if it doesn't exist. """
    if not collection_exists(collection_name):
        create_collection(collection_name, parent_collection, link)

    return _obj_to_collection(collection_name, obj)


def _obj_to_collection(collection_name: str, obj: bpy.types.Object, from_collection=None) -> bool:
    """ Internal: Links object to target collection. """
    for col in obj.users_collection:
        if col.name == collection_name:
            continue
        col.objects.unlink(obj)
        collection = bpy.data.collections.get(collection_name)
        collection.objects.link(obj)
    return True


def get_child_collections(col_name: str):
    """ Returns array of child collection names or parent name if no children found. """
    # attempt to get child collections
    if not collection_exists(col_name):
        return [col_name]

    collection = bpy.data.collections.get(col_name)
    if collection.children > 0:
        return [col.name for col in collection.children]

    return [col_name]


def get_objects_from_collection(col_name):
    """ Returns objects from collection. """
    if collection_exists(col_name):
        col = bpy.data.collections[col_name]
        return [ob for ob in col.all_objects]
    else:
        return None


def move_list_to_collection(to_collection: str, objects: List[bpy.types.Object], from_collection: str = None) -> None:
    """ Move list of elements from, to a collection. """
    assert from_collection is not None
    for ob in objects:
        _obj_to_collection(to_collection, ob, from_collection)
