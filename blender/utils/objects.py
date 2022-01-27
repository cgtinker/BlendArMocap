import bpy


# region OBJECTS
# region GENERATE EMPTY
def add_empties(data: dict, size, extension=""):
    return [add_empty(size=size, name=value+extension) for key, value in data.items()]


def add_empty(size, name, display='ARROWS'):
    ob = get_object_by_name(name)
    if ob is not None:
        return ob

    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = size
    obj.empty_display_type = display
    return obj


def get_object_by_name(name):
    try:
        ob = bpy.data.objects[name]
        return ob
    except KeyError:
        return None


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
def hide_collection_viewport(col_name, status):
    if collection_exists(col_name):
        collection = bpy.data.collections.get(col_name)
        collection.hide_viewport = status


def collection_exists(col_name):
    if bpy.data.collections.get(col_name) is not None:
        return True
    else:
        return False


def create_collection(col_name, parent_col, link=True):
    if collection_exists(col_name):
        return False

    else:
        collection = bpy.data.collections.new(col_name)

        if link:
            if parent_col is None:
                bpy.context.scene.collection.children.link(collection)
            else:
                create_collection(parent_col, None, True)
                parent = bpy.data.collections.get(parent_col)
                parent.children.link(collection)
        return True


def remove_collection(col_name, remove_objects):
    if collection_exists(col_name):
        collection = bpy.data.collections.get(col_name)
        if collection:
            if remove_objects:
                obs = [o for o in collection.objects if o.users == 1]
                while obs:
                    bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(collection)


def add_list_to_collection(col_name, objects, parent_col=None, link=True):
    if not collection_exists(col_name):
        create_collection(col_name, parent_col, link)

    for o in objects:
        link_obj_to_collection(o, col_name)


def add_obj_to_collection(col_name, m_object, parent_col=None, link=True):
    if not collection_exists(col_name):
        create_collection(col_name, parent_col, link)
    link_obj_to_collection(m_object, col_name)


def link_obj_to_collection(m_object, name):
    # todo: add proper fix
    try:
        bpy.context.scene.collection.objects.unlink(m_object)
        collection = bpy.data.collections.get(name)
        collection.objects.link(m_object)
    except RuntimeError:
        pass


def get_child_collections(col_name):
    """ returns array of child collection names or parent name if no children found. """
    # attempt to get child collections
    if collection_exists(col_name) and len(bpy.data.collections[col_name].children) > 0:
        return [col.name for col in bpy.data.collections[col_name].children]
    # if no children return active col name
    else:
        return [col_name]


def get_objects_from_collection(col_name):
    """ returns objects from collection. """
    if collection_exists(col_name):
        col = bpy.data.collections[col_name]
        return [ob for ob in col.all_objects]
    else:
        return None
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
    constraint.source = target_obj
    constraint.use_offset = use_offset


def add_copy_rotation_constraint(obj, target_obj, invert_y):
    constraint = obj.constraints.new('COPY_ROTATION')
    constraint.source = target_obj
    if invert_y:
        constraint.invert_y = True
# endregion


def get_frame_start():
    try:
        frame_start = bpy.context.scene.frame_start
    except AttributeError:
        return 0
    return frame_start
