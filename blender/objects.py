import bpy


def generate_empties(data: dict, size):
    empties = []
    for key, value in data.items():
        obj = bpy.data.objects.new(value, None)
        bpy.context.scene.collection.objects.link(obj)

        obj.empty_display_size = size
        obj.empty_display_type = 'ARROWS'

        empties.append(obj)
    return empties

