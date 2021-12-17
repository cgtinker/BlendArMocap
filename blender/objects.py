import bpy
from mathutils import Vector


# region OBJECTS
# region GENERATE EMPTY
def add_empties(data: dict, size, extension=""):
    return [add_empty(size=size, name=value+extension) for key, value in data.items()]


def add_empty(size, name, display='ARROWS'):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = size
    obj.empty_display_type = display
    return obj


def add_camera(name):
    camera_data = bpy.data.cameras.new(name=name)
    camera_object = bpy.data.objects.new(name, camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    return camera_object
# endregion


# region SELECTION
def is_object_selected():
    objects = len(bpy.context.selected_objects)
    if objects >= 1:
        return True
    else:
        return False


def get_selected_object():
    objects = len(bpy.context.selected_objects)

    if objects >= 1:
        return bpy.context.selected_objects[0]
# endregion


# region ACTIONS
def set_parents(parent, children):
    [set_parent(parent, child) for child in children]


def set_parent(parent, child):
    child.parent = parent
# endregion
# endregion


# region COLLECTIONS
def hide_collection_viewport(name, status):
    if collection_exists(name):
        collection = bpy.data.collections.get(name)
        collection.hide_viewport = status


def collection_exists(name):
    for collection in bpy.data.collections:
        if collection.name == name:
            return True
    return False


def create_collection(name, link):
    if collection_exists(name):
        return False
    else:
        collection = bpy.data.collections.new(name)
        if link:
            bpy.context.scene.collection.children.link(collection)
        return True


def remove_collection(name, remove_objects):
    if collection_exists(name):
        collection = bpy.data.collections.get(name)
        if collection:
            if remove_objects:
                obs = [o for o in collection.objects if o.users == 1]
                while obs:
                    bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(collection)


def add_list_to_collection(name, objects):
    if not collection_exists(name):
        create_collection(name, True)

    for o in objects:
        link_obj_to_collection(o, name)


def add_obj_to_collection(name, m_object):
    if collection_exists(name):
        link_obj_to_collection(m_object, name)

    create_collection(name, True)
    link_obj_to_collection(m_object, name)


def link_obj_to_collection(m_object, name):
    bpy.context.scene.collection.objects.unlink(m_object)
    collection = bpy.data.collections.get(name)
    collection.objects.link(m_object)
# endregion


# region CLEANUP
def purge_orphan_data():
    # remove all orphan data blocks
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    # remove all orphan armatures
    for armature in bpy.data.armatures:
        print(armature)
        if armature.users == 0:
            print("remove;", armature)
            bpy.data.armatures.remove(armature)
# endregion


# region ARMATURE
def add_armature(name):
    arm = bpy.data.armatures.new(name)
    return arm


def get_armature(name="face_armature"):
    armature = bpy.data.objects[name]
    return armature


def get_armature_bones(armature):
    bones = armature.data.bones
    return bones


def get_armature_edit_bones(armature):
    bones = armature.data.edit_bones
    return bones


def get_global_bone_position(armature, bone):
    global_position = bone.head_local + armature.location
    return global_position


def get_global_bone_head_position(armature, bone):
    global_location = armature.matrix_world @ bone.head_local
    return global_location
# endregion


# region CONSTRAINTS
def add_copy_location_constraint(obj, target_obj, use_offset):
    constraint = obj.constraints.new('COPY_LOCATION')
    constraint.target = target_obj
    constraint.use_offset = use_offset


def add_copy_rotation_constraint(obj, target_obj, invert_y):
    constraint = obj.constraints.new('COPY_ROTATION')
    constraint.target = target_obj
    if invert_y:
        constraint.invert_y = True
# endregion
